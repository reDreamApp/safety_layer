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
**Phase 2 (Safety Module):** Complete — graph, classifier, critic all working, benchmarked
**Phase 3 (Integration):** Not started — hook SafetyCritic into irt_app.py

**Immediate TODO:**
- Run benchmark with META sanity check fix, compare results
- Generate and run test set for generalization validation
- Post-hoc manual annotation pass on generated dataset
- Research how to handle irrelevant/trolling user inputs (e.g., off-topic, nonsense, adversarial prompts in rewriting stage)
- **Run full-set semantic consistency benchmark (N=5, all 480 dev cases) for S1 and S2.** Targeted run on error+control slice (Apr 14) showed consistency fixes 65% of S1 errors / 83% of S2 errors with zero regressions and gives a usable UQ signal for S2 (agreement separation 0.255 vs 0.012 from logprobs). Need full-set run to confirm the "zero broken cases" property on all previously-correct predictions before closing out the UQ chapter. Est. ~2h for S1, ~5.4h for S2. See `docs/planning/System2_CoT_Findings.md` §8.

**Completed:**
- Removed all ZDPCS references
- Fixed confidence estimation in classifier
- Codebase restructuring (Feb 17, 2026)
- Change 1.3: Added SUPPRESSION (DENY) and TRAUMA_REPLAY (REPLAY) maladaptive nodes (Feb 17, 2026)
- Regenerated dev benchmark dataset with GPT-5.4 (480 tests, 12 nodes) (Mar 19, 2026)
- Full dev benchmark: 95.0% safety accuracy, 98.3% unsafe recall (Mar 19, 2026)
- META sanity check: catches maladaptive content in meta-framed inputs during rescripting (Mar 19, 2026)
- Added GPT-5.4 model config, made max_tokens configurable on Agent (Mar 19, 2026)
- Fixed multipart test cases to include expected_node for node-level evaluation (Mar 19, 2026)
- Detailed changelog: `docs/planning/Changes_2026-03-19.md`

**Open questions:**
- Awaiting ontology validation from Dr. Annika Gieselmann
- Confidence threshold: analyzed, stays at 0.0 (see Changes_2026-03-19.md §9 for rationale)
- Adversarial/trolling input handling strategy

## Key Clinical Context
- **Maladaptive patterns** (unsafe): Avoidance/flight, Interruption/waking, Violent revenge, Suppression/denial, Trauma Replay/re-experiencing
- **Adaptive patterns** (safe/goals): Behavioral, Social, Environmental, Emotional, Mythical mastery (from MMS — Germain 2004)
- The safety layer must catch maladaptive rescripting and redirect toward adaptive alternatives
- Key references: Germain et al. 2004 (MMS), Krakow & Zadra 2006 (IRT protocol), DSM-5 PTSD criteria
- Detailed clinical rationale: `docs/clinical/Clinical_Ontology_Scientific_Rationale.md`
