#!/usr/bin/env python3
"""
opportunity-scout ENGINE (script-driven, cron-safe).

Pipeline (fast, request-efficient, ~1 model call per run):
  1. Run a bounded, rotating set of Tavily web searches.
  2. Collect + dedupe candidate results (title, url, snippet).
  3. ONE model call judges ALL candidates against the fit criteria and returns
     a strict JSON array of only the genuine, funded, on-domain matches.
  4. Hand that JSON to deliver.py -> dedup vs local ledger -> Airtable -> email.

Why script-driven: a fully-agentic search/read/verify loop makes dozens of model
turns and blows past time/rate limits on free tiers. This keeps model usage to a
single batched call, so it's fast and reliable under cron.

Stdlib only. Reads keys from ~/.hermes/.env (Tavily, Gemini, OpenRouter).
Usage:
  python3 scout.py                 # normal run (search -> judge -> deliver)
  python3 scout.py --queries 8     # run more/fewer searches this pass
  python3 scout.py --dry-run       # search + judge + PRINT, no deliver side effects
  python3 scout.py --no-deliver    # search + judge, just write run_candidates.json
"""
import os, sys, json, re, subprocess, datetime
import urllib.request, urllib.error, urllib.parse

HOME = os.path.expanduser("~/.hermes")
SCRIPTS = os.path.join(HOME, "skills", "opportunity-scout", "scripts")
REPORTS = os.path.join(HOME, "reports")
CAND_PATH = os.path.join(REPORTS, "run_candidates.json")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-3-flash-preview"
OR_BASE = "https://openrouter.ai/api/v1"
OR_MODELS = ["openai/gpt-oss-120b:free", "nvidia/nemotron-3-ultra-550b-a55b:free"]

# Rotating query bank — a run uses a slice, so different days surface different angles.
# PRIMARY MISSION = fully-funded standalone MASTER'S (research/thesis MSc) in active
# LLM-inference/MLSys research groups & communities. NOT PhDs, and NOT integrated
# MSc->PhD / direct-PhD-track programs. Industry jobs and PhDs each get their own
# separate module later so they don't crowd out or get mislabeled against funded MSc study.
QUERY_BANK = [
    "fully funded master's LLM inference optimization thesis",
    "funded MSc thesis position machine learning systems MLSys",
    "fully funded master's efficient deep learning efficient NLP",
    "KV cache paged attention research group funded master's thesis",
    "vLLM OR TensorRT-LLM OR SGLang research lab funded MSc student",
    "quantization speculative decoding funded master's thesis MLSys",
    "GPU inference serving systems research funded master's scholarship",
    "Erasmus Mundus scholarship machine learning AI systems master's",
    "DAAD OR government scholarship fully funded master's machine learning",
    "fully funded MSc machine learning systems Europe Netherlands",
    "fully funded master's machine learning Canada Australia scholarship",
    "research master's MSc by research machine learning systems funded",
    "fully funded master's computer science AI scholarship 2026 2027",
    "funded thesis-based master's efficient LLM inference research group",
]


def load_env():
    p = os.path.join(HOME, ".env")
    if not os.path.exists(p):
        return
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip(); v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
            v = v[1:-1]
        os.environ.setdefault(k, v)


def pick_queries(n):
    # Rotate the window start by ONE each day so, over len(QUERY_BANK) days, every
    # angle gets used. (The old `day * n % len` only ever yielded 2 fixed slices when
    # gcd(n, len) > 1 — e.g. n=7, len=14 → always 0 or 7.)
    day = datetime.date.today().toordinal()
    start = day % len(QUERY_BANK)
    return [QUERY_BANK[(start + i) % len(QUERY_BANK)] for i in range(min(n, len(QUERY_BANK)))]


def tavily_search(query, max_results=5):
    key = os.environ.get("TAVILY_API_KEY", "")
    body = json.dumps({
        "api_key": key, "query": query, "search_depth": "basic",
        "max_results": max_results, "include_answer": False,
    }).encode()
    req = urllib.request.Request("https://api.tavily.com/search", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        d = json.load(urllib.request.urlopen(req, timeout=30))
        out = []
        for r in d.get("results", []):
            out.append({"title": (r.get("title") or "").strip(),
                        "url": (r.get("url") or "").strip(),
                        "snippet": (r.get("content") or "").strip()[:600]})
        return out
    except Exception as e:
        print(f"  [warn] Tavily search failed for {query!r}: {type(e).__name__}: {e}")
        return []


JUDGE_INSTRUCTIONS = """You are screening web search results for a specific person, Haseeb,
a CS undergraduate (finishing 6th semester) looking for FUNDED GRADUATE STUDY.

HE WANTS (the ONLY thing this pipeline collects): a fully-funded standalone MASTER'S
(research/thesis MSc) in an active research group / lab / community working on LLM
INFERENCE OPTIMIZATION / ML SYSTEMS (MLSys), a systems + empirical angle. Strong topics: LLM inference/serving
efficiency, KV-cache management/compression, paged
attention, vLLM/TensorRT-LLM/SGLang/TGI, quantization/low-bit inference, speculative
decoding, MoE inference, GPU memory management for DL, efficient transformers/attention,
distributed/parallel INFERENCE, MLSys/systems-for-ML. Adjacent-OK: multi-agent LLM
systems, RAG, applied NLP with a strong systems/empirical component.

DROP (do NOT return these):
- PhD positions of any kind. This pipeline is MASTER'S ONLY. Drop standalone PhD openings.
- INTEGRATED / COMBINED MSc-PhD programs, direct-PhD-entry / fast-track-to-PhD tracks, and
  anything advertised as "Master's leading to a PhD" (admission bundles the doctorate).
  NOTE: a normal standalone funded MSc that a student *could later* separately apply to a
  PhD from is FINE — only DROP programs that bundle/require the PhD commitment.
- INDUSTRY JOBS / paid positions of ANY kind — engineer/researcher/intern roles at
  companies (NVIDIA, ByteDance, Microsoft, Together, etc.). This pipeline is funded STUDY
  only; jobs are handled elsewhere. A salaried job is NOT "funding".
- Pure-theory ML/stats with no systems angle; non-LLM AI unrelated to his work (pure
  computer vision, robotics, RL) unless it clearly overlaps efficient inference/serving;
  anything non-CS; anything NOT a funded degree; anything clearly off-topic.

RULES:
- Keep ONLY a genuine fully-funded standalone MASTER'S place (or an active research group
  advertising funded MSc/master's-thesis openings in the domain).
- "Fully funded" means tuition covered + a stipend/scholarship/grant — NOT a salary.
- type is ALWAYS "Master's". Never output "PhD", "Job", or any other type — if it isn't a
  standalone funded master's, drop it.
- Regions: worldwide is fine — do not drop a strong match for its location.
- Prefer authoritative sources (university/department/lab/official funding pages). Be
  skeptical of vague aggregator/social-media listings; keep only if it looks real.
- If unsure whether it truly fits or is funded, either drop it or set confidence "Low".

Return ONLY a JSON array (no prose, no markdown fences). Each element:
{"title","url","type","university","country","professor","why_fits","funding","confidence"}
where type is always "Master's", funding in [Fully funded,Partial,Unclear],
confidence in [High,Medium,Low], why_fits is ONE short sentence. If nothing qualifies,
return []."""


def _extract_json_array(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()
    if not text.startswith("["):
        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            text = m.group(0)
    return json.loads(text)


def call_gemini(prompt):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        return None
    url = f"{GEMINI_BASE}/models/{GEMINI_MODEL}:generateContent?key={key}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": {"temperature": 0.2}}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        d = json.load(urllib.request.urlopen(req, timeout=120))
        return d["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  [warn] Gemini judge failed: {type(e).__name__}: {e}")
        return None


def call_openrouter(prompt):
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        return None
    for model in OR_MODELS:
        body = json.dumps({"model": model,
                           "messages": [{"role": "user", "content": prompt}],
                           "temperature": 0.2}).encode()
        req = urllib.request.Request(f"{OR_BASE}/chat/completions", data=body,
                                     headers={"Authorization": f"Bearer {key}",
                                              "Content-Type": "application/json"}, method="POST")
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            if "choices" in d:
                print(f"  [info] judged via OpenRouter fallback: {model}")
                return d["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  [warn] OpenRouter {model} failed: {type(e).__name__}: {e}")
    return None


def judge(candidates):
    payload = [{"title": c["title"], "url": c["url"], "snippet": c["snippet"]}
               for c in candidates]
    prompt = (JUDGE_INSTRUCTIONS + "\n\nSEARCH RESULTS (JSON):\n" +
              json.dumps(payload, ensure_ascii=False))
    text = call_gemini(prompt) or call_openrouter(prompt)
    if not text:
        print("  [error] no model available to judge candidates.")
        return None
    try:
        arr = _extract_json_array(text)
        if isinstance(arr, list):
            return arr
        print("  [warn] model did not return a JSON array.")
    except Exception as e:
        print(f"  [warn] could not parse model output as JSON: {e}")
    return None


def main():
    load_env()
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    no_deliver = "--no-deliver" in argv
    nq = 7
    if "--queries" in argv:
        try:
            nq = int(argv[argv.index("--queries") + 1])
        except Exception:
            pass

    os.makedirs(REPORTS, exist_ok=True)
    queries = pick_queries(nq)
    print(f"scout: running {len(queries)} searches")
    candidates, seen = [], set()
    for q in queries:
        res = tavily_search(q)
        print(f"  search: {q!r} -> {len(res)} results")
        for r in res:
            u = re.sub(r"[?#].*$", "", r["url"].lower()).rstrip("/")
            if u and u not in seen and r["title"]:
                seen.add(u); candidates.append(r)
    print(f"scout: {len(candidates)} unique candidates -> judging with one model call")

    if not candidates:
        print("scout: no candidates found; nothing to do.")
        return

    vetted = judge(candidates)
    if vetted is None:
        print("scout: judging failed; aborting without delivery.")
        sys.exit(2)
    print(f"scout: model kept {len(vetted)} vetted opportunity(ies)")

    with open(CAND_PATH, "w", encoding="utf-8") as f:
        json.dump(vetted, f, ensure_ascii=False, indent=2)
    print(f"scout: wrote {CAND_PATH}")

    if no_deliver:
        print("scout: --no-deliver, stopping before delivery.")
        return

    cmd = [sys.executable, os.path.join(SCRIPTS, "deliver.py")]
    if dry:
        cmd.append("--dry-run")
    cmd.append(CAND_PATH)
    print(f"scout: handing off to deliver.py ({'dry-run' if dry else 'live'})")
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
