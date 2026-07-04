---
name: opportunity-scout
description: "Discover fully-funded standalone Master's (research/thesis MSc) opportunities in LLM inference optimization / ML systems (funded MSc is the ONLY thing collected; PhDs, integrated MSc->PhD tracks, and industry jobs are out of scope / separate future modules), verify them, and deliver new finds to Airtable + email. Use for the recurring opportunity-discovery run."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, opportunities, funding, mlsys, discovery, aggregation]
    related_skills: [arxiv]
---

# Opportunity Scout

Recurring discovery + aggregation of **fully-funded standalone Master's** opportunities
(research / thesis MSc) in active LLM-inference / MLSys research groups & communities —
this is the **primary and only mission of this pipeline**. Deliberately **out of scope
here** (each a separate future module or excluded): standalone **PhDs**, **integrated /
combined MSc→PhD** or direct-PhD-track programs ("Master's leading to a PhD"), and
**industry jobs**. A normal funded MSc a student could *later* separately pursue a PhD
from is fine; a program that *bundles* the PhD commitment is not. Your persona, the fit
criteria, target keywords, regions, and hard boundaries are already defined in
`SOUL.md` and `~/.hermes/RESEARCH.md` — **follow them exactly**. This skill is the
step-by-step run.

## Boundaries (non-negotiable — current phase)
- **Discovery + aggregation ONLY.** Do NOT draft or send outreach emails, and do NOT
  apply to anything. The only email that goes out is the automated digest **to Haseeb**,
  sent by `deliver.py` (not by you).
- Only **public** information goes into searches and outputs. Never put his personal
  profile/CV details into a web search or any external service.
- Stay **request-efficient** — free-tier API limits are real (see Step 2 caps).

## Prerequisites
- `web` tool available (Tavily). Check with a trivial search if unsure.
- Delivery env vars set (Airtable + email). `deliver.py` handles missing ones gracefully.

## Workflow

### Step 1 — Load targeting
Re-read `~/.hermes/RESEARCH.md` for the current keyword list, non-matches, and region
preferences (favorites first, but **open worldwide** — never discard a strong match for
being outside the favorites). **Degree scope:** standalone funded **Master's ONLY**
(`type: "Master's"`). Drop PhDs and integrated MSc→PhD / direct-PhD tracks.

### Step 2 — Search (bounded, rotate to stay efficient)
Run **6–8 web searches this run** — do not exhaust every query every time. Rotate across
these angles so different runs surface different things:

Core query bank (combine a domain term with a region/scope):
- `fully funded master's LLM inference optimization <region>`
- `funded MLSys / machine learning systems master's thesis <region>`
- `KV cache / efficient LLM inference research group master's <region>`
- `vLLM OR TensorRT-LLM OR SGLang lab hiring funded students`
- `quantization / speculative decoding research group funded master's`
- `GPU inference serving systems funded master's / MSc scholarship`
- `scholarship fully funded master's machine learning systems 2026/2027`
- `research master's / MSc by research machine learning systems funded <region>`

Regions to cycle through favorites first, then broaden: Netherlands, wider Europe,
Canada, Australia, New Zealand, then global (US, UK, Singapore, etc.).

For each search: scan results, keep only ones plausibly matching the domain + funded +
in-scope. **Prefer authoritative domains** (university/department/lab pages, official
funding/scholarship calls, reputable job boards). Treat social-media / aggregator hits as
leads to verify, not evidence.

### Step 3 — Verify promising leads
For each promising lead, use `web_extract` (or a follow-up search) to confirm:
- **Funding** — is it actually fully funded (tuition + stipend / grant / scholarship)?
- **Active research** — is the professor/lab **currently publishing** in the domain
  (recent papers/projects)? Cross-check with the `arxiv` skill if useful.
- **Live, correct link** — the URL resolves to the real opportunity/lab page.
Drop anything you cannot verify. A short high-precision list beats a long noisy one.

### Step 4 — Judge fit & assemble results
For each verified opportunity, judge fit against the SOUL heuristic and assign
`confidence` (High/Medium/Low). Build a JSON array with this exact schema:

```json
[
  {
    "title": "Fully-funded MSc position in efficient LLM inference",
    "url": "https://university.edu/...",
    "type": "Master's",
    "university": "Example University",
    "country": "Netherlands",
    "professor": "Prof. X / Y Lab",
    "why_fits": "Lab publishes on KV-cache compression & vLLM serving; MSc is funded.",
    "funding": "Fully funded",
    "confidence": "High"
  }
]
```
Rules: `title` and `url` are required. `type` is ALWAYS `Master's` (PhDs, integrated
MSc→PhD tracks, and industry jobs are NOT collected here — drop them). `funding` means
tuition + stipend/scholarship/grant — a salary is not funding. `funding` ∈ Fully funded|Partial|Unclear.
`confidence` ∈ High|Medium|Low. Keep `why_fits` to one line. Write the JSON to
`~/.hermes/reports/run_candidates.json`.

### Step 5 — Deliver (dedup + Airtable + email)
Run the helper — it dedupes against the local ledger and only acts on genuinely NEW
opportunities (appends to CSV, creates Airtable rows, sends ONE email digest):

```bash
python3 ~/.hermes/skills/opportunity-scout/scripts/deliver.py ~/.hermes/reports/run_candidates.json
```
(Add `--dry-run` first if you want to preview what's new without side effects.)

### Step 6 — Report
Summarize briefly: how many searched, how many verified, how many were new vs already
known, and the headline finds. Note any searches skipped due to rate limits.

## Notes
- The CSV ledger `~/.hermes/reports/opportunities.csv` is the dedup memory + backup —
  never delete it. Airtable is the browsable record; email is the notification.
- If `web` searches start returning 429 / rate-limit errors, stop early, deliver what you
  have, and note it — do not hammer the API.
