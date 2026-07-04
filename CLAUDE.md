# CLAUDE.md — Hermes Agent Project Context

> **Read this first.** This file explains what we're building, why, where things
> stand right now, and what I need your help with. Follow the guardrails at the
> bottom. When in doubt, propose a plan and wait for my confirmation before making
> big changes — I like to review step by step.

---

## 1. Your role vs. the agent's "brain" (don't confuse these)

There are **two different AIs** in this project. Keep them straight:

- **You (Claude Code) = the builder / mechanic.** You write and edit config, prompts,
  and skills; you run commands and test things. You are running on my Claude **Pro**
  plan. You are *not* the thing that runs the agent day to day.
- **Hermes's runtime model = the engine.** At runtime, Hermes uses **free models via
  OpenRouter + Google Gemini** (details in §5) to actually do the research work. That
  is a separate system from you.

So: **you help me set up and configure Hermes. The OpenRouter/Gemini models are what
Hermes uses once it's running.** Don't try to wire yourself in as the runtime model.

---

## 2. The mission (what we're building)

A **self-hosted personal research-and-outreach agent** using **Hermes Agent** (by Nous
Research), running on this VPS. Its long-term job:

1. **Find fully-funded master's / research opportunities** — locate professors who are
   *actively publishing and researching* in my domain, primarily in **Europe (incl. the
   Netherlands), Canada, Australia, and New Zealand**.
2. **Find relevant job openings** in the same fields/regions.
3. **Aggregate these opportunities** from multiple sources into a clean, reviewable list
   for me.
4. **Later:** draft and send personalized outreach emails to professors, and help apply
   on my behalf.

The end goal is landing a **fully-funded master's placement** through targeted outreach.

---

## 3. Current phase — IMPORTANT scope limit (July–August 2026)

We are in a **light testing + aggregation phase only.** Real applications start in
**September**, which is when this gets serious.

**In scope right now:**
- Get the agent working end to end.
- Build and test the **discovery + aggregation** workflow (find & collect opportunities
  from multiple sources).
- Keep everything on **free models** and low/no cost.

**Explicitly OUT of scope right now (do NOT build/enable yet):**
- Drafting or sending any emails.
- Applying to anything on my behalf.
- Feeding any of my personal/confidential info (CV, personal details) to the free models.

We'll add the email-drafting + sending phase in September, and it will use a **paid**
model then (better writing quality for professor emails). Not now.

---

## 4. System / environment

- **Host:** Hetzner VPS, `ubuntu-4gb-hel1-1`, Ubuntu 24.04 LTS
- **Resources:** ~2 vCPU, **4 GB RAM**, no GPU → **keep everything lightweight**; do not
  install heavy dependencies or try to run any local LLM (it won't fit).
- **User:** running as the unprivileged `hermes` user (has sudo). Not root.
- **Config home:** `~/.hermes/` (this is your working directory).
- **Terminal backend:** Local (Docker sandbox is a *later* hardening step, before we ever
  send real emails — not needed now).

---

## 5. Hermes Agent — current state

Installed and healthy (`hermes doctor` passes). Key facts:

- **Version:** Hermes Agent v0.18.0, Python 3.11 in its own venv.
- **Installed with `--skip-browser`** → Playwright Chromium is *not* installed, so
  `browser_*` tools are hidden. That's fine for now (we're using web/search tools, not
  full browser automation). Flag it if a task truly needs a headless browser.
- **Core tools working:** `terminal`, `file`, `memory`, `cronjob`, `code_execution`,
  `skills`, `todo`, `session_search`, `delegation`, `project`, `clarify`.
- **Not yet configured:** the model provider (the brain). **This is the first real task.**

Key paths under `~/.hermes/`:
- `.env` — API keys and provider settings
- `config.yaml` — main config (models, providers, fallbacks)
- `SOUL.md` — the agent's persona / mission brief (system prompt)
- `skills/` — custom skills/workflows
- `cron/` — scheduled jobs
- `memories/`, `sessions/`, `logs/`

---

## 6. The model setup (the agent's brain) — decided plan

**Phase-now = FREE models only.** Chosen chain, primary → fallbacks:

- **Primary:** `nvidia/nemotron-3-ultra-550b-a55b:free`
  *(frontier reasoning + orchestration, 1M context — best free fit for reading long
  funding pages/professor bios and judging relevance)*
- **Fallback 1:** `openai/gpt-oss-120b:free` *(different provider → separate rate-limit pool)*
- **Fallback 2:** `nousresearch/hermes-3-llama-3.1-405b:free`
- **Independent second source:** **Google Gemini free tier** (via AI Studio),
  e.g. `gemini-3-flash` — used as a separate provider so we're not dependent on one pool.
- **Optional failsafe:** OpenRouter's `openrouter/free` auto-router, which auto-picks an
  available free model that supports the features a request needs (incl. tool calling).

**Why free is OK for this phase:** the discovery/aggregation work only touches **public**
info (professors, labs, funding calls, job posts). Free models may log/train on inputs,
which is acceptable for public data — but **that's exactly why we do NOT send personal
data or draft emails on free models.** Email drafting waits for a paid model in September.

**Rate-limit reality (design for this):** OpenRouter free tier ≈ 20 req/min and
50 req/day (rises to ~1,000/day once ≥ $10 credit has been added); Gemini free ≈ 1,500
req/day. So **make workflows request-efficient** — batch where possible, avoid needless
loops, and lean on the fallback chain when one source rate-limits.

---

## 7. What I need your help with (task backlog, in order)

1. **Wire up the model provider.** Configure OpenRouter in `~/.hermes/.env` and
   `config.yaml` with the primary + fallback chain from §6. I'll give you the
   `OPENROUTER_API_KEY`. Add **Gemini** as a second provider too (I'll give the AI Studio
   key). Then verify with `hermes doctor` (API Connectivity line) and a quick test session.
2. **Write the mission brief (`SOUL.md`).** Read `PROFILE.md`, `PROJECTS.md`, and
   `RESEARCH.md` (§9) first, then write a sharp persona + task definition so the agent
   knows *exactly* what a "good opportunity" is, using the criteria in `RESEARCH.md`
   §"What a Good Opportunity Looks Like" as the core filter logic.
3. **Build the discovery + aggregation skill(s).** A workflow that searches multiple
   sources (professor/lab pages, university funded-master's & PhD calls, scholarship
   databases, relevant job boards) for my fields + target countries, and collates results
   into a clean, deduplicated, reviewable list (e.g., a markdown/CSV report in a known
   location). Keep it request-efficient (§6).
4. **Schedule it (light cadence).** Set up a cron job to run the discovery workflow on a
   gentle schedule (e.g., once or twice daily) and save results for me to review. Nothing
   aggressive — this is the light phase.
5. **Stop there.** Email drafting/sending and applications are the September phase.

---

## 8. Guardrails / rules for you

- **Confirm before big changes.** Propose a plan, let me approve, then act. Small edits
  are fine to just do.
- **Keep it lightweight** — 4 GB RAM. No heavy installs, no local models.
- **No emails, no applications, no personal data to free models** in this phase (§3).
- **Be request-efficient** with the free-tier rate limits (§6).
- **Plain language, step by step.** Explain what you're doing concisely; I'm learning as
  we go and want to understand each step.
- **Don't hardcode secrets** into `config.yaml` or skills — keep keys in `.env`.
- If a task needs the browser tools (not installed) or a paid model, **flag it and pause**
  rather than working around it silently.

---

## 9. Context files — READ THESE before building SOUL.md (task 2)

✅ The §9 gaps are now filled via three additional context files, also in `~/.hermes/`.
**Read all three before writing or editing `SOUL.md`:**

- **`PROFILE.md`** — who I am: education (NUST, currently 6th semester standing,
  GPA 3.78), work experience, skills.
- **`PROJECTS.md`** — my portfolio, including the CUST Hackathon 2026 win (160+ teams,
  "Bideez" multi-agent RFP pipeline) and my LLM inference optimization repo.
- **`RESEARCH.md`** — **the most important one for search targeting.** My exact research
  domain (LLM inference optimization / ML systems), the specific keywords to search on,
  what does NOT match, confirmed target regions, degree scope (Master's primary, PhD
  acceptable if flagged separately), and the "what makes a good opportunity" heuristic.

Still outstanding:
- **Specific target universities/professors** — none named yet (see `RESEARCH.md`); agent
  should proactively surface strong candidates rather than waiting to be told names.
- **API keys** (I'll give these in chat, add them to `.env`): OpenRouter key, Gemini
  (AI Studio) key.

---

## 10. How to test / useful commands

```bash
hermes doctor        # health + which providers/keys are configured
hermes model         # interactive model/provider setup wizard
hermes               # start an interactive session with the agent
```

Quick sanity check after wiring the model: start a session and give it a simple,
tool-using task (e.g., "search the web for one funded master's call in my field in the
Netherlands and summarize it") to confirm the brain + tools + fallbacks work.

---

*Phase: light testing & aggregation (Jul–Aug 2026). Serious applications begin September.*
