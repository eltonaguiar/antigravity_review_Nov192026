# Reviewer roster — who is actually worth asking, measured

Every reviewer here has been run on the **same** questions (the R01b brief, F2/F3, or the fund-script audit).
Quality is recorded as **observed behaviour on a specific task**, not as a benchmark score or a reputation.

**Standing rule:** a review is judged on whether it **recomputed** something. Fluency, headings and a limitations section
cost a model nothing and predict nothing.

---

## What is reachable, and without what

| surface | access | models | how I drive it |
|---|---|---|---|
| **Ollama (local, GPU)** | free, no key | `qwen3-vl:2b/4b/8b`, `devstral:24b`, `llama3.1:8b`, `starcoder2:15b`, `hermes-desktop` | `POST http://127.0.0.1:11434/api/chat` |
| **vLLM (local, GPU)** | free, no key | `Qwen3.6-35B-A3B-NVFP4` (16 K ctx) | `POST http://127.0.0.1:8000/v1/chat/completions` |
| **Router (local)** | free, no key | aliases `ULTRA_FREE_CLOUD_LARGE` etc. | `:4000/v1` — **returned 0 chars twice on the long brief**, falls back to `ollama:qwen3:8b` |
| **free.ai** | free, **no signup** | 27 models, 3 tiers; free self-hosted = `Qwen 3.6 35B` + `Qwen 3.6 35B Thinking`; standard/premium need purchased tokens | browser (profile copy), native value setter + real click |
| **chatplayground.ai** | free | ChatGPT-6 Luna, Claude (Latest), Qwen3.6 Flash, GLM 5.3 Flash | CDP — **accepts 8 K-char pastes** |
| **askanymodel.xyz** | free | 6 panes, user-swappable | CDP, charges credits per ask |
| **1min.ai** | free, credits refill | Gemini 4 Neon, GPT-4.1 mini, Claude, Qwen | CDP; mic = audio-muted button, never click |
| **arena.ai** | free | frontier models, side-by-side | CDP |
| **GitHub Models** | **BLOCKED** | — | `models.github.ai` returns `200 text/plain "OK"` (4 bytes) on both `/catalog/models` and `/inference/chat/completions` with the `gh` OAuth token. Measured, not assumed: not provisioned for this account. |
| **imagera.ai** | paywalled per question | — | skipped by operator decision |
| **benchlm.ai** | free | 1,035 models × 835 benchmarks | model *selection* only, no chat |

## Key-gated options worth adding, best first

1. **OpenRouter free tier** — one key, ~13 free models (DeepSeek, Llama, Qwen, Gemma, Mistral, GLM), OpenAI-compatible, so it
   drops straight into `ask_free_ais.py`. Highest value by a wide margin: it makes the roster **programmatic** instead of
   browser-driven.
2. **HuggingFace Inference Providers** — the operator is already signed in; a read token unlocks a monthly free allowance
   across many providers.
3. **Google AI Studio** — generous free tier, Gemini family.
4. **Groq / Cerebras** — free tiers, very fast, small model set.

Keys are not to be pasted in chat. Drop the value in a file (e.g. `~/.openrouter_key`) and I will wire it in from there.

---

## Measured behaviour on our own questions

| reviewer | task given | what it did | verdict on the reviewer |
|---|---|---|---|
| **Gemini 4 Neon** (Google AI, 110,052 credits) | audit the fund script | found 4 defects, identified the double-counted MER, reproduced the retracted 17 bp to 0.4 bp, named the settling test | **the best reviewer used today.** Recomputed instead of restating |
| **devstral:24b** (local) | F2 / F3 adversarial | F2 SOLID with a *correct* falsifier (if round-trip cost < 6.4 bp the claim falls). F3 OVERSTATED on portfolio grounds: "an unreachable bracket can be a legitimate choice to avoid significant losses" | **useful and context-blind.** The challenge is real but at the wrong layer — it judges a *portfolio* decision when F3 is a *scoring-rule* decision. A conservative book and a mean-R contest are not the same object |
| **GPT-4.1 mini** (OpenAI, 14,720 credits) | review the fund deep-dive | endorsed the retracted claim as the "primary actionable insight", listed "accounting for actual fees" as a **strength**, recommended FXAIX over SPY, and listed the falsifying significance test as future work | **amplifier.** Fluent, structured, wrong — see `REVIEW_AMPLIFICATION_2026-11-23.md` |
| **ollama qwen3:8b** (local) | full F1–F6 brief | returned all six verdicts twice with near-identical wording; F1's falsifier was circular ("a strategy that avoids voids by predicting future prices"), F3's reason restated the claim then called it wrong | **formulaic.** Verdict-shaped output, no engagement. Not evidence |
| **router `ULTRA_FREE_CLOUD_LARGE`** | full brief | returned **0 chars** on the long brief; had also fallen back to `ollama:qwen3:8b` on an earlier call | **not usable on long inputs** — and it masquerades as a second reviewer |
| **chatplayground ×4** | page review | all four refused a bare URL ("I can't browse"), which is honest; accepted the pasted 8,156-char page and generated | **workable once you paste** |
| **free.ai ×2 (Qwen 3.6 35B, 35B Thinking)** | full brief | accepted the prompt after switching both panes to free; still generating at time of writing | pending |

## Two things this roster changes

1. **Never count a panel as N reviewers until each answer names a different model.** Two of my "three panels" were
   `qwen3:8b` reported twice, and the router's own alias contributed nothing.
2. **Ask the expensive model to audit and the cheap model to summarise.** The pattern in this single day — one observation,
   not a rule — is that the 7.5×-more-expensive model found the arithmetic error and the cheap one wrapped the error in
   headings.

## Prerequisite for any local reviewer

`torch` here is **2.10.0+cpu with `cuda` unavailable**, so a transformers-based model would run on CPU and be impractical
for anything multimodal. GPU local inference goes through **Ollama** or **vLLM**, both already serving. `transformers 5.1.0`
is installed and Python 3.12/3.13 are available if a CUDA build is ever wanted, but the serving paths already exist and
don't need it.

`qwen2.5-coder:14b` (~9 GB Q4, fits 12 GB VRAM) is being pulled as the local **code-audit** model — the one task where a
small model can still be genuinely useful, because the check is mechanical.

*Paper only. No live orders, no credentials in repo. Not investment advice.*
