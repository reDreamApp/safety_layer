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
**Phase 3 (Integration):** Complete — SafetyCritic hooked into `AI/irt_app.py` (fail-open init, evaluation during rewriting stage, nightmare summary generation). Integration surfaced flow-breaking issues (redirect loop, stage-transition blocking, summary sanitization) — **documented as findings, not fixed** (see `docs/planning/integration_eval_notes.md`). Rationale: modifying the base system would confound the safety-vs-baseline comparison.
**Phase 4 (Evaluation + Writing):** In progress

**Immediate TODO:**
- **Run full-set semantic consistency benchmark (N=5, all 480 dev cases) for S1 and S2.** Targeted run on error+control slice (Apr 14) showed consistency fixes 65% of S1 errors / 83% of S2 errors with zero regressions and gives a usable UQ signal for S2 (agreement separation 0.255 vs 0.012 from logprobs). Need full-set run to confirm the "zero broken cases" property on all previously-correct predictions before closing out the UQ chapter. Est. ~2h for S1, ~5.4h for S2. See `docs/planning/System2_CoT_Findings.md` §8.
- **Generate single-turn eval dataset** for system-level eval (thesis §4.5) — LLM responses with/without safety layer for expert rating.
- **Obtain expert annotation** from Dr. Annika Gieselmann (currently awaiting Fragebogen feedback) and Katharina Lüth (IRT researcher, Osnabrück) on test set — for IRR on the targeted-annotated slice.
- **Thesis writing** — skeleton at `docs/planning/thesis_skeleton.md` (18 figures planned; 3 exist, ~8 need creation).

**Completed:**
- Removed all ZDPCS references
- Fixed confidence estimation in classifier
- Codebase restructuring (Feb 17, 2026)
- Change 1.3: Added SUPPRESSION (DENY) and TRAUMA_REPLAY (REPLAY) maladaptive nodes (Feb 17, 2026)
- Regenerated dev benchmark dataset with GPT-5.4 (480 tests, 12 nodes) (Mar 19, 2026)
- Full dev benchmark (post-fix deterministic segmenter + classifier, Apr 23–24, 2026):
  - S1 baseline: 97.86% safety accuracy, 99.44% unsafe recall
  - S1 consistency (N=5): 97.86% safety accuracy, 99.44% unsafe recall
  - S2 baseline: 98.10% safety accuracy, 99.44% unsafe recall
  - S2 consistency (N=5): **98.81% safety accuracy (best), 98.33% unsafe recall** — precision/recall trade-off
  - Pre-fix runs (Mar 23–25, Apr 20–22) archived to `data/benchmarks/archive/pre_fix/`
- Segmenter determinism fix (Apr 22–23, 2026): switched `safety/critic.py` segmenter to `MISTRAL_NEMO` (Scaleway-direct) + `temperature=0`. OR aggregator routing across heterogeneous backends was the dominant driver of run-to-run segment drift (5–6/6 regression cases pre-fix → 2/6 with clear majority modes post-fix). Determinism probe + diagnosis in `docs/planning/System2_CoT_Findings.md` §10.3.1; post-fix headline numbers in §11.
- Transient-error retry logic added to `AI/agent.py` (4 attempts, exponential backoff) — resolves sporadic Scaleway connection drops seen during long consistency runs.
- META sanity check: catches maladaptive content in meta-framed inputs during rescripting (Mar 19, 2026)
- Added GPT-5.4 model config, made max_tokens configurable on Agent (Mar 19, 2026)
- Fixed multipart test cases to include expected_node for node-level evaluation (Mar 19, 2026)
- System 2 (CoT) classifier + logprobs/semantic-consistency UQ comparison (Mar 25, 2026)
- Context-aware few-shot ablation — negative result, documented (Mar 25, 2026)
- Targeted semantic consistency on error+control slice (Apr 14, 2026)
- Test set generated (315 cases, 7 themes) + targeted human annotation pass by Ramon: 114 cases (all boundary, all AFFECT_EXPRESSION, all VIOLENT_REVENGE, 60-case stratified spot-check across 10 nodes) (Apr 13–16, 2026)
- SafetyCritic integrated into `AI/irt_app.py`; integration eval findings documented (Apr 17, 2026)
- Ontology validated by Dr. Annika Gieselmann
- Detailed changelog: `docs/planning/Changes_2026-03-19.md`

**Scoped out of thesis (documented as future work):**
- Adversarial/trolling input handling — initial test suggested the system handles it; not pursued further
- S2 BEHAVIORAL_MASTERY → AVOIDANCE failure pattern — documented as a limitation / negative finding in thesis §4.4; ensemble design (S1 primary + S2 second-opinion on low-conf) avoids the issue without requiring a fix
- Ensemble approach (S1 primary + S2 second opinion + semantic consistency on S2) — proposed in `System2_CoT_Findings.md` §6.5, not implemented
- Integration fixes (redirect loop, stage-aware constraint injection, safe-but-faithful summarization) — future work; see `integration_eval_notes.md`

**Open items:**
- Fragebogen feedback from Dr. Gieselmann (ontology itself already validated)
- Expert annotation from Gieselmann + Lüth on test set
- Confidence threshold: analyzed, stays at 0.0 (see Changes_2026-03-19.md §9 for rationale)

## Key Clinical Context
- **Maladaptive patterns** (unsafe): Avoidance/flight, Interruption/waking, Violent revenge, Suppression/denial, Trauma Replay/re-experiencing
- **Adaptive patterns** (safe/goals): Behavioral, Social, Environmental, Emotional, Mythical mastery (from MMS — Germain 2004)
- The safety layer must catch maladaptive rescripting and redirect toward adaptive alternatives
- Key references: Germain et al. 2004 (MMS), Krakow & Zadra 2006 (IRT protocol), DSM-5 PTSD criteria
- Detailed clinical rationale: `docs/clinical/Clinical_Ontology_Scientific_Rationale.md`
