
# RESEARCH.md — My Research Interest & Target Domain (for Hermes / Claude Code context)

> **This is the most important file for search targeting.** Use it to judge whether a
> professor/lab/funding call is actually a good fit — don't just match on "AI" broadly,
> match on the specific sub-area below.

---

## Core Research Interest: LLM Inference Optimization

This is my primary, active research direction — I'm currently doing independent work in
this area and want to continue it at the graduate level.

**What I've actually done** (see `PROJECTS.md` for full detail, repo:
github.com/bilalrana351/llm-inference-optimization):
- Reproducible, **measured** benchmarking of LLM inference: **HuggingFace Transformers
  vs. vLLM** on a single GPU (not just reading papers — running real, measured
  comparisons).
- A deliberate **KV-cache out-of-memory (OOM) experiment**, with the failure point
  plotted against an **analytical prediction** — i.e., building a model of *when* memory
  should run out and checking it against what actually happens.

This shows my specific angle: **systems-level, empirical rigor** around how LLMs are
served/deployed efficiently — not just training bigger models, but making inference
*fast, memory-efficient, and predictable at scale.*

## Field / Domain Classification

For search purposes, this sits at the intersection of:
- **Machine Learning Systems (MLSys)**
- **Efficient Deep Learning / Efficient NLP**
- **Computer Systems** (applied to ML workloads)
- Broader umbrella: **Artificial Intelligence / Natural Language Processing**, but with a
  **systems/efficiency** angle, not a pure modeling/algorithms angle.

## Specific Sub-Topics & Keywords to Search On

When looking for professors, labs, funded positions, or job postings, prioritize these
terms (roughly in order of relevance to my work):

- LLM inference optimization / efficient LLM inference
- KV cache management / KV cache compression / paged attention
- vLLM, TensorRT-LLM, SGLang, TGI (inference serving frameworks)
- Model serving, inference serving systems, LLM serving infrastructure
- GPU memory management for deep learning
- Quantization (LLM quantization, low-bit inference)
- Speculative decoding
- Mixture-of-Experts (MoE) inference efficiency
- Efficient Transformers / efficient attention mechanisms
- ML systems, systems for machine learning, MLSys
- Distributed/parallel inference, tensor parallelism, pipeline parallelism (as applied to
  inference, not just training)

**Secondary/adjacent interests** (relevant, but not my current core focus — still worth
surfacing if a lab spans both): multi-agent LLM systems, RAG systems, applied NLP,
general AI/ML with a strong empirical/systems component.

## What Does NOT Match (help filter noise)

Deprioritize or flag as lower-fit:
- Pure theory-only ML/statistics research with no systems or empirical inference
  component.
- Non-LLM AI subfields unrelated to my work (e.g., pure computer vision, robotics,
  reinforcement learning) — unless a specific opportunity explicitly overlaps with
  efficient inference/serving.
- Non-CS/non-technical fields entirely.

## Degree Scope

- **Primary target: fully-funded Master's** (thesis-based/research-track preferred over
  coursework-only, since the goal is to continue this research direction).
- **Also acceptable: funded PhD** positions, if a strong fit — flag these separately so I
  can consider them (they're a bigger commitment, so don't auto-merge with Master's
  results).

## Target Regions (preferred, NOT exclusive)

**Open to opportunities worldwide** — do not restrict the search to a fixed region list.
The regions below are *preferences* to prioritize and to use as tiebreakers, not filters.
A genuinely strong, funded, well-matched opportunity anywhere in the world is welcome and
should be surfaced.

Preferred (lean toward these):
1. **Europe** (including the Netherlands specifically — lightly prioritize NL on a tiebreak)
2. **Canada**
3. **Australia**
4. **New Zealand**

Within Europe, no specific country exclusions.

## Universities / Professors Already on My Radar

*(None specific yet — this is open. As I identify names, they'll be added here. Hermes
should proactively surface strong MLSys/efficient-inference groups at well-known
programs in the target regions — e.g., groups known for systems-for-ML work — rather
than waiting for me to name them first.)*

## What a "Good Opportunity" Looks Like (summary heuristic)

A result is a strong match if it hits **most** of:
1. Professor is **actively publishing/researching** (recent papers/projects, not dormant)
   in LLM inference efficiency, ML systems, or closely adjacent efficient-NLP work.
2. Position is **fully funded** (tuition + stipend, or clearly funded via grant/scholarship).
3. Located in one of the four target regions.
4. Degree is **Master's** (or flagged separately if PhD).
5. Lab/group has visible infrastructure or track record suggesting real systems/empirical
   work (not purely theoretical).

---

*Update this file as my research direction sharpens (e.g., after reading more papers or
after Sept when applications get serious) — it directly controls search quality.*
