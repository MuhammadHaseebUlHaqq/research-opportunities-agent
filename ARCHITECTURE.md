# Architecture

## Overview

The agent is a **script-driven pipeline** wrapped in a Hermes skill. The heavy lifting is
done by two stdlib-only Python scripts so the whole run is fast, reliable, and cheap under
cron — a single batched model call per run rather than a chatty agentic loop.

```
                         ┌──────────────────────────────────────────┐
                         │            scout.py  (engine)            │
                         │                                          │
  cron (daily 20:00 PKT) │  1. pick_queries()  ── rotating slice ── │
        │                │        of the Master's-only query bank   │
        ▼                │  2. tavily_search() × N  (web tool)      │
   python3 scout.py ────▶│  3. dedupe candidates by normalized URL  │
                         │  4. judge()  ── ONE model call ──────────│
                         │        Gemini (primary)                  │
                         │          └─ fallback ─▶ OpenRouter free   │
                         │        → strict JSON: standalone Master's │
                         │  5. write reports/run_candidates.json     │
                         └───────────────────┬──────────────────────┘
                                             │ hand off vetted JSON
                                             ▼
                         ┌──────────────────────────────────────────┐
                         │           deliver.py  (I/O only)         │
                         │                                          │
                         │  • dedupe vs reports/opportunities.csv   │
                         │  • append NEW rows to the CSV ledger     │
                         │  • create Airtable row per new find      │
                         │  • send ONE Gmail digest (STARTTLS:587)  │
                         └──────────────────────────────────────────┘
```

## Why script-driven (not fully agentic)

A fully-agentic search → read → verify loop makes dozens of model turns and blows past
time and rate limits on free tiers. Collapsing the judgment into **one batched call over
all candidates** keeps the run fast and predictable — ideal for an unattended cron job.

## The two goals split cleanly

- **`scout.py`** owns *discovery + judgment* (the "brain": what counts as a real,
  funded, standalone Master's in the domain).
- **`deliver.py`** owns *deterministic I/O* (dedup, ledger, Airtable, email). No model
  calls, no judgment — so delivery is boringly reliable.

## The model chain

| Role | Provider | Model | Why |
|------|----------|-------|-----|
| Primary judge | Gemini (free tier) | `gemini-3-flash-preview` | Fast, ~1M context, strong tool/JSON output |
| Fallback 1 | OpenRouter (free) | `openai/gpt-oss-120b:free` | Different pool → survives Gemini throttles |
| Fallback 2 | OpenRouter (free) | `nvidia/nemotron-3-ultra-550b-a55b:free` | Heaviest reasoning, last resort |

If the primary times out or rate-limits, `scout.py` automatically falls through the chain.

## Dedup & idempotency

The CSV ledger `reports/opportunities.csv` is the dedup memory. Keys are normalized URLs
(query/fragment stripped, lowercased). A re-run over the same finds produces `new=0` — no
duplicate emails, no duplicate Airtable rows. This is what makes the daily cron safe.

## Data / secret boundaries

- Only **public** opportunity info flows into searches and outputs.
- All credentials live in `.env` (never in `config.yaml` or the scripts).
- The scripts parse `.env` like `python-dotenv` (a value with spaces is kept whole), so a
  pasted Gmail app password won't be mangled.
