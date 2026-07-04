# research-opportunities-agent

A self-hosted personal **research-and-outreach agent**, built on
[Hermes Agent](https://github.com/NousResearch) (by Nous Research), that discovers
**fully-funded standalone Master's** opportunities in **LLM inference optimization /
ML systems (MLSys)**, verifies them, and delivers new finds to an Airtable base + a daily
email digest.

> **Status:** light discovery + aggregation phase. It *finds and collects* opportunities —
> it does **not** email professors or apply on anyone's behalf. Outreach is a later,
> paid-model phase.

---

## What it does

Once a day it:

1. Runs a bounded, rotating set of web searches (Tavily) for funded Master's positions in
   the target domain + regions.
2. Judges **all** candidates in a single model call (Gemini primary, OpenRouter free
   models as fallback) against a strict fit heuristic — keeping only genuine, funded,
   standalone Master's matches.
3. Deduplicates against a local CSV ledger and, for each **new** find, writes an Airtable
   row and includes it in one email digest.

**Scope of this pipeline:** standalone funded **Master's only**. PhDs, integrated
MSc→PhD / direct-PhD tracks, and industry jobs are intentionally excluded (jobs and PhDs
may become their own separate modules later).

---

## Repository layout

| Path | What it is |
|------|------------|
| `SOUL.md` | The agent's persona + mission brief (system prompt). The fit heuristic lives here. |
| `config.yaml` | Hermes model/provider config — free primary + fallback chain. **Keys are referenced by env var, never hardcoded.** |
| `.env.example` | Template for the secrets the agent needs. Copy to `.env` and fill in. |
| `skills/opportunity-scout/SKILL.md` | The discovery workflow (agentic description). |
| `skills/opportunity-scout/scripts/scout.py` | Cron-safe engine: search → one batched judge call → hand off to delivery. |
| `skills/opportunity-scout/scripts/deliver.py` | Deterministic delivery: dedup → CSV ledger → Airtable → email digest. |
| `cron/opportunity-scout.cron` | The daily schedule (documented crontab line). |
| `PROFILE.md`, `PROJECTS.md`, `RESEARCH.md` | Personal context: who it's searching for, and the exact research-targeting spec. |
| `CLAUDE.md`, `PLAN.md` | Project context and build plan. |

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for how the pieces fit together.

---

## Setup

This is designed to run under a Hermes Agent install (`~/.hermes/`). To reproduce:

1. Install [Hermes Agent](https://github.com/NousResearch) (`--skip-browser` is fine —
   this uses Tavily for search, not full browser automation).
2. Drop `SOUL.md`, `config.yaml`, and `skills/opportunity-scout/` into your `~/.hermes/`.
3. `cp .env.example .env` and fill in your **free-tier** keys (see the file for where to
   get each).
4. Verify: `hermes doctor` should show your providers + the `web` tool as available.

### Running the scout manually

```bash
# full run: search -> judge -> dedup -> deliver (CSV + Airtable + email)
python3 skills/opportunity-scout/scripts/scout.py

# preview only: search + judge, no CSV/Airtable/email side effects
python3 skills/opportunity-scout/scripts/scout.py --dry-run

# search + judge, just write the vetted JSON (no delivery)
python3 skills/opportunity-scout/scripts/scout.py --no-deliver

# widen/narrow the search this run
python3 skills/opportunity-scout/scripts/scout.py --queries 10
```

### Scheduling

See `cron/opportunity-scout.cron`. The default cadence is **once daily at 20:00 PKT
(15:00 UTC)** — a gentle pace that stays well within free-tier limits.

---

## Design principles

- **Zero spend.** Only free model slugs (OpenRouter `:free`) and free provider tiers
  (Gemini, Tavily). No paid routes in this phase.
- **Request-efficient.** One batched model call per run; bounded, rotating searches.
- **Precision over volume.** A short, high-confidence list beats a long noisy one — some
  days there will be **no** new find, and that's correct behavior.
- **Secrets stay in `.env`**, never in config or code.

See [`CHANGELOG.md`](./CHANGELOG.md) for the build history and
[roadmap](./CHANGELOG.md#roadmap).
