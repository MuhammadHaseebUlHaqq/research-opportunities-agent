# PROJECTS.md — Portfolio Highlights (for Hermes / Claude Code context)

> Use this to understand my practical/applied strengths. Relevant when judging fit for
> AI/ML/systems-oriented research groups or jobs, and later when it's time to
> reference concrete work in outreach.

---

## Most Recent / Most Relevant

### Bideez — Multi-Agent RFP Pipeline (CUST Hackathon 2026 Winner) 🏆
**GitHub:** github.com/bilalrana351/bideez

- Won **1st place** at the **CUST Hackathon 2026** — one of Pakistan's biggest hackathons,
  **160+ competing teams**.
- Built a **multi-agent pipeline** for RFP (Request for Proposal) handling, with stages:
  **decide → create → verify → defend**.
- Includes **human-in-the-loop gates** (checkpoints where a human approves/steers before
  the pipeline continues) — relevant to agentic-systems and human-AI collaboration work.
- Uses **pgvector RAG** (PostgreSQL vector search + retrieval-augmented generation) for
  grounding.
- Includes a **voice rehearsal mode** (practicing/defending a proposal via voice
  interaction).
- Demonstrates: multi-agent orchestration, RAG systems, human-in-the-loop design,
  voice AI integration — shipped and working under hackathon time pressure.

### LLM Inference Optimization (Independent Research / Current Interest)
**GitHub:** github.com/bilalrana351/llm-inference-optimization

- **This is my core research interest area — see RESEARCH.md for full detail.**
- Reproducible, *measured* (not just theoretical) comparison of **HuggingFace vs vLLM**
  inference baselines on a single GPU.
- Includes a **deliberate KV-cache out-of-memory (OOM) experiment**, with results plotted
  against the **analytical prediction** — i.e., not just "it broke," but modeling *why*
  and *at what point* it breaks and checking the model against real behavior.
- Demonstrates hands-on systems-level understanding of LLM serving internals: KV-cache
  memory growth, throughput/latency tradeoffs, paged attention style serving (vLLM),
  and rigor in comparing empirical results to analytical models.

---

## Other Notable Projects

### CareerPrep — AI-Powered Career Preparation Platform
- FastAPI backend, resume parsing/skill extraction via Groq LLM, automated job matching,
  voice-based AI mock interview assistant, Supabase-backed REST APIs.
- Built end-to-end within a hackathon timeframe.

### BotVerse — RAG-Based Multi-Bot Chatbot Platform
- FastAPI + LangChain, Pinecone vector search, embeddable per-site chatbots with isolated
  knowledge bases, optional React admin panel.

### IntakeAI — Voice AI for Healthcare Appointment Booking
- Vapi AI + Deepgram (STT) + Cartesia (TTS) + GPT-3.5 Turbo, direct CRM scheduling
  integration. Next.js frontend + C++ Glade desktop GUI.

### PitchVision — AI Football Performance Analysis
- OpenCV + YOLOv5 for player detection/tracking from match video; generates
  player-specific performance statistics for coaching decisions.

### Forest Cover Type Prediction (ML)
- Multi-class classification comparing Logistic Regression, SVM, KNN, Random Forest,
  XGBoost, LightGBM, Extra Trees with hyperparameter tuning; ~0.88–0.89 validation
  accuracy; deployed via Streamlit.

### AutoSense — Text Autocompletion + Sentiment Analysis
- Trie-based autocomplete in C++ with Qt GUI; Naive Bayes sentiment classifier built
  from scratch; integrated via a Python Flask API.

### RideTogether — Campus Carpooling Platform
- React + Node.js/Express + MongoDB, Leaflet.js maps, JWT/Bcrypt auth.

---

*When judging "is this professor/lab a good fit," weight most heavily: LLM inference
optimization work (my primary research direction), the multi-agent/RAG systems work
(Bideez, BotVerse), and applied ML deployment experience.*
