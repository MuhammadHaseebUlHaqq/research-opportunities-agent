# Changelog

Build history of the research-opportunities-agent (light discovery phase).

## Phase 1 — discovery & aggregation

### Model provider wired
- Configured the free model chain in `config.yaml`: **Gemini `gemini-3-flash-preview`**
  primary (chosen after Nemotron 550B proved too slow for agentic web work), with an
  OpenRouter free-tier fallback chain (`gpt-oss-120b:free` → `nemotron-3-ultra-550b:free`
  → `hermes-3-llama-405b:free`).
- Pinned all auxiliary tasks to the free Gemini tier so no request silently routes to a
  paid model. **Zero-spend** is a hard constraint this phase.

### Web search enabled
- Wired the `web` tool via **Tavily** (free tier ~1,000 searches/mo) for search + extract.

### Mission brief
- Wrote `SOUL.md`: persona, the fit heuristic ("what a strong opportunity looks like"),
  domain keywords, target regions (preferred, not exclusive), and hard phase boundaries.

### Discovery skill
- Built `skills/opportunity-scout/` — `SKILL.md` workflow + `scout.py` engine +
  `deliver.py` delivery helper (CSV ledger → Airtable → email digest).
- Verified end-to-end: live search → judge → dedup → CSV + Airtable + email all fired;
  a re-run produced `new=0`, proving dedup keeps the daily cron from re-spamming.

### Tuning
- **Fixed** the `pick_queries` daily rotation (it previously only ever yielded two fixed
  query slices).
- **Refocused** queries + judge onto funded *study*, removing industry-job noise that had
  been getting mislabeled as "Fully funded."
- **Narrowed to standalone Master's only** — excluding PhDs, integrated/combined MSc→PhD
  and direct-PhD-track programs. (A funded MSc one could *later* separately pursue a PhD
  from still qualifies; a program that *bundles* the PhD does not.)
- **Widened coverage** — bumped Tavily results per search from 5 → 10 (no extra cost;
  Tavily bills per request, not per result).

### Scheduling
- Daily cron at **20:00 PKT / 15:00 UTC** (`cron/opportunity-scout.cron`).

---

## Roadmap

- **Jobs module** — a separate pipeline for relevant industry roles (kept out of the
  Master's pipeline so the two don't cross-contaminate).
- **Source-quality hardening** — prefer authoritative university/lab pages over social
  posts; resolve leads to their official source before trusting them.
- **Primary-judge robustness** — raise the Gemini timeout / trim batch size so the primary
  model does the judging even on large candidate sets.
- **Outreach phase (later, paid model)** — draft and send personalized professor emails.
  Deliberately out of scope now.
