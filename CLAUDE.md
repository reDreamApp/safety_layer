# ReDream AI — Neuro-Symbolic Safety Layer for IRT Chatbot

## What This Is
Master's thesis project (Ramon Zacharias). An AI chatbot for Imagery Rehearsal Therapy (IRT) — nightmare rescripting — with a neuro-symbolic safety layer that detects maladaptive dream content and redirects toward therapeutic goals.

## Project Structure
```
AI/              — IRT chatbot agent, API, prompts (NOT thesis focus — minimize changes)
safety/          — Safety critic pipeline (THESIS FOCUS)
  graph_definitions.py  — Clinical knowledge graph (MMS/IRT ontology)
  classifier.py         — LLM-based entity linker (text → graph nodes)
  critic.py             — Clinical Reasoning Engine (segment → classify → triage → constrain)
experiments/     — Benchmarking + dataset generation scripts
tests/           — All tests (pytest + interactive test scripts)
data/
  scenarios/     — Test scenario JSON files (nightmare contexts + test cases)
  benchmarks/    — CSV/JSON benchmark datasets
  results/       — Test result outputs
docs/            — All documentation (architecture, planning, clinical, dataset, references)
papers/          — Research PDFs (gitignored)
```

## Dev Commands
```bash
uv run pytest tests/                           # run tests
uv run python -m AI.api                        # start FastAPI server
uv run python experiments/run_benchmark.py     # run benchmarks
uv run python tests/test_critic_interactive.py --scenario data/scenarios/chase_scenario_tests.json -v
```

## Conventions
- Use `uv` for all Python (venv, deps, running). Dependencies in pyproject.toml.
- Conventional commits
- Always include tests for new functionality
- Imports: `from AI.agent import Agent`, `from safety.critic import SafetyCritic` (packages at repo root)

## Architecture (3-Block Pipeline)
1. **Knowledge Graph** (Block A, `safety/graph_definitions.py`): Clinical ontology — 5 maladaptive nodes (Avoidance, Interruption, Violent Revenge, Suppression, Trauma Replay) + 5 MMS adaptive nodes + 2 neutral nodes, connected by 15 correction edges
2. **Entity Linker** (Block B, `safety/classifier.py`): LLM-based classifier mapping user text to graph nodes, with negation handling, ambiguity rules, context-aware emotional suppression detection
3. **Critic Pipeline** (Block C, `safety/critic.py`): Intelligent segmentation → META filtering → batch classification → severity triage → "Validate + Correct" constraint synthesis

## Current State
**Phase 1 (Setup):** Complete
**Phase 2 (Safety Module):** Complete — graph, classifier, critic all working
**Phase 3 (Integration):** Not started — hook SafetyCritic into irt_app.py

**Immediate TODO (from TODO_Changes_2026-02-17.md):**
- After code changes: regenerate benchmark datasets
- Research how to handle irrelevant/trolling user inputs (e.g., off-topic, nonsense, adversarial prompts in rewriting stage)

**Completed:**
- Removed all ZDPCS references
- Fixed confidence estimation in classifier
- Codebase restructuring (Feb 17, 2026)
- Change 1.3: Added SUPPRESSION (DENY) and TRAUMA_REPLAY (REPLAY) maladaptive nodes to graph_definitions.py, classifier.py, critic.py, tests, scenarios, and docs (Feb 17, 2026)

**Open questions:**
- Awaiting ontology validation from Dr. Annika Gieselmann
- [update this section as needed]

## Key Clinical Context
- **Maladaptive patterns** (unsafe): Avoidance/flight, Interruption/waking, Violent revenge, Suppression/denial, Trauma Replay/re-experiencing
- **Adaptive patterns** (safe/goals): Behavioral, Social, Environmental, Emotional, Mythical mastery (from MMS — Germain 2004)
- The safety layer must catch maladaptive rescripting and redirect toward adaptive alternatives
- Key references: Germain et al. 2004 (MMS), Krakow & Zadra 2006 (IRT protocol), DSM-5 PTSD criteria
- Detailed clinical rationale: `docs/clinical/Clinical_Ontology_Scientific_Rationale.md`
