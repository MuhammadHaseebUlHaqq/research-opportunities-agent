# PLAN.md — Hermes Setup & Discovery Build (Light Phase, Jul–Aug 2026)

> Living checklist. We execute phase by phase; you review each step.
> Scope reminder: discovery + aggregation of **public** opportunity info only.
> **No emails, no applications, no personal data to free models** until the Sept/paid phase.

---

## Context snapshot (verified from your files)

- **Who:** Muhammad Haseeb Ul Haq — BS CS, NUST SEECS, GPA 3.78. **6th semester completed;
  on summer break now; 7th semester starts Sept 2026** (halfway through the degree, not final year).
  Sept also = when applications get serious, so this break's build is the groundwork.
- **Core research direction:** **LLM inference optimization** (KV-cache, paged attention,
  vLLM/TensorRT-LLM/SGLang, quantization, speculative decoding, MoE inference, MLSys) —
  systems + empirical angle, not pure theory/modeling.
- **Degree scope:** fully-funded **Master's** primary (thesis/research-track preferred);
  funded **PhD** acceptable but **flagged separately**, never auto-merged with Master's.
- **Regions:** Europe (incl. Netherlands — light tiebreak priority), Canada, Australia, NZ.
- **Universities/professors:** none named yet — agent should **proactively surface**
  strong MLSys/efficient-inference groups.
- **Good-opportunity heuristic:** actively-publishing prof in the domain + fully funded +
  in-region + Master's (or flagged PhD) + visible systems/empirical track record.

## Current system state (verified)

- Hermes v0.18.0, healthy, Python 3.11 venv. Installed `--skip-browser` (no Playwright).
- `config.yaml` `model.default` = `anthropic/claude-opus-4.6` (PAID — must change to free).
- `.env` has all keys **commented out**; slots exist for `OPENROUTER_API_KEY`,
  `GOOGLE_API_KEY`/`GEMINI_API_KEY`.
- `SOUL.md` = generic factory default (no mission yet).

---

## Phase 1 — Wire up the brain (free-model provider) · ✅ DONE (2026-07-04)
- [x] 1.1 Keys added to `.env` by user (OpenRouter + Gemini, Gemini in a fresh project).
- [x] 1.2 **Primary = `gemini-3-flash-preview` via `provider: gemini`** (user-chosen after
      testing showed Nemotron 550B too slow for agentic multi-turn web work — timed out at
      300s; Gemini Flash did the same task in seconds).
- [x] 1.3 Fallback chain via `fallback_providers` (list IS supported): 1) nemotron-550b:free
      (heaviest reasoning), 2) gpt-oss-120b:free, 3) hermes-3-llama-3.1-405b:free — all
      OpenRouter (separate pool → catches Gemini per-minute throttles). Confirmed via
      `hermes fallback list`.
- [x] 1.4 All 13 `auxiliary.*` tasks pinned to native Gemini free (they otherwise default
      to PAID `google/gemini-3-flash-preview` via OpenRouter and would spend credit).
- [x] 1.5 All `:free` slugs confirmed live on OpenRouter; Gemini Flash confirmed via API.
- [x] 1.6 `hermes doctor`: API Connectivity ✓ OpenRouter + ✓ gemini. Backups:
      `config.yaml.bak.phase1.*`.

## Phase 2 — Confirm discovery toolchain · ✅ DONE (2026-07-04)
- [x] 2.1 Web search enabled via **Tavily** (`TAVILY_API_KEY` in `.env`; free ~1,000/mo).
      `hermes doctor` Tool Availability → `web` ✓. Browser tools remain unavailable
      (`--skip-browser`) — not needed; Tavily does search + extract.
- [x] 2.2 End-to-end verified: default config (Gemini Flash) ran the agent, did a live
      Tavily search, and returned real on-target results (TU Delft AISE lab NL; Queen's
      Univ. Canada). Brain + web search + domain targeting all working together.
- Note for Phase 4: model picks weak sources sometimes (e.g. a Facebook post) — the
  discovery skill must constrain to quality sources (university domains, scholarship DBs).

## Phase 3 — Mission brief (`SOUL.md`) · ✅ DONE (2026-07-04)
- [x] 3.1 Installed persona from `PROFILE.md` / `PROJECTS.md` / `RESEARCH.md`
      (backup: `SOUL.md.bak.default.*`).
- [x] 3.2 Encoded the "good opportunity" filter: domain keywords + non-matches,
      funded-only, actively-publishing prof, systems/empirical track record,
      Master's goal with PhD flagged separately.
- [x] 3.3 Regions = **preferred, not exclusive** (open worldwide; favorites =
      Europe/NL, Canada, Australia, NZ as tiebreak). Synced same change into `RESEARCH.md`.
- [x] 3.4 Hard boundaries baked in: no emails, no applying, no personal data sent
      externally; source-quality discipline (verify vs official sources, drop weak leads).

## Phase 4 — Discovery + aggregation skill · context READY (needs Phase 2)
- [ ] 4.1 Multi-source search: lab/prof pages, funded Master's/PhD calls, scholarship DBs,
      relevant job boards — for the domain keywords × target regions.
- [ ] 4.2 Dedupe + rank by the heuristic; PhD results flagged separately.
- [ ] 4.3 Write clean markdown/CSV report to a known location.
- [ ] 4.4 Request-efficient by design (free-tier ~20 req/min, ~50 req/day OpenRouter;
      batch, no needless loops, lean on fallback).

## Phase 5 — Light cron schedule
- [ ] 5.1 Cron job, once/twice daily, saves report for review. Nothing aggressive.

## STOP — September / paid phase (not now)
- Email drafting + sending, applications, personal data → paid model, later. Do not build.

---

## Key/model test results (2026-07-04)
- **OpenRouter key: WORKING.** Primary `nvidia/nemotron-3-ultra-550b-a55b:free` replied cleanly.
  Fallbacks `openai/gpt-oss-120b:free` + `nousresearch/hermes-3-llama-3.1-405b:free`
  authenticated but hit **429 upstream rate-limit** at test time (transient free-tier
  busyness — the reason the fallback chain exists; not an error to fix).
- **All three OpenRouter free slugs confirmed live.**
- **Gemini key: BLOCKED.** Can list models, but generation returns **403 PERMISSION_DENIED
  "project has been denied access"** across ALL Gemini models (native + OpenAI-compat).
  Google-side project/account issue, not our config. Correct current slug is
  `gemini-3-flash-preview` (the plan's `gemini-3-flash` does not exist).
- **Security:** both keys were accidentally printed to the session transcript during
  testing → **rotate both keys**; when regenerating the Gemini key, make it under a NEW
  Google project (may also clear the 403).

## Open questions / risks tracked
- Multi-step fallback chain support in Hermes config (Phase 1.3).
- Web-search tool + whether an API key is required (Phase 2.1).
- Free model slugs drift — re-verify at execution (Phase 1.5).
