# Handoff: Phase 4 System-Level Eval (§4.5)

You're picking up the ReDream AI thesis project to build the held-out test-set system-level eval (thesis §4.5). This is the eval that gets expert-rated by Dr. Annika Gieselmann and Katharina Lüth — the integration-eval pilot from Apr 23–27 was the dry run.

## Quick context

ReDream AI = Master's thesis (Ramon Zacharias) — neuro-symbolic safety layer for an IRT nightmare-rescripting chatbot. Project root: `/Users/sunray/projects/thesis/claude`. Repo conventions: `CLAUDE.md`. All commands via `uv`.

Phase 3 integration is complete (`AI/irt_app.py`, see Phase 3 entry in CLAUDE.md). Tweak A (empty-VALIDATE suppression on HIGH/CRITICAL) shipped 2026-04-27 (commit `3e9b267`) — the production constraint now emits a `NO_VALIDATE` block when `adaptive_segments=[]` AND severity ∈ {HIGH, CRITICAL}, with a tightened IMPORTANT bullet against "taking action" reframings. **Do not revert this** — it has passing smoke tests and was a clinical-correctness fix, not a numbers-tuning fix.

The integration-eval pilot (`docs/planning/HANDOFF_INTEGRATION_EVAL.md`, results in `data/integration_eval/`) ran the same A/B harness on the dev set with an LLM-as-judge. Its job per its handoff was to *"validate the constraint-redirect mechanism end-to-end before the Phase 4 expert-rated system eval."* That job is done. **The pilot's findings are documented in `docs/planning/integration_eval_notes.md`** (two 2026-04-27 addendums) — read these before you start so you don't re-discover them. Key findings: (a) asymmetric Δ across nodes, (b) constraint redundancy on VR (base prompt covers it), (c) template-collapse + empty-VALIDATE leak on SUP/TR (Tweak A partially addressed), (d) lexical bans don't generalize, (e) headline numbers move within sampling noise at temp=0.5, N=5/cell.

**Gap this eval fills:** §4.5 of the thesis claims the safety system improves the chatbot's responses on *held-out* data, judged by *clinical experts*. The pilot used dev data and an LLM judge; the §4.5 eval needs the test set and Gieselmann/Lüth.

## Three deliverables

### Deliverable 1 — Re-run benchmark on the test set with the current critic

`data/benchmarks/test_benchmark_results.csv` exists from 2026-04-14, but that's pre-segmenter-fix (Apr 22–23) and pre-Tweak-A (Apr 27). Selecting scenarios by a stale classifier signal would mis-attribute — re-run.

**Action:**
```bash
# Single-pass on the primary evaluation set (267 cases = 315 - 48 buried-alive).
# The buried-alive suite was excluded by Ramon (GPT-5.4 content-filter truncation;
# see test_annotation_log.json metadata.summary.excluded_suite).
uv run python experiments/run_benchmark.py \
    --dataset data/benchmarks/test_dataset.json \
    --output data/benchmarks/test_benchmark_results_postfix.csv
```

If `--dataset`/`--output` aren't existing flags on `run_benchmark.py`, peek at the script to find the right invocation. Don't run with `--consistency 5` unless you have ~3h to spare; single-pass is enough for selection. If you want a UQ signal too, run consistency in background overnight.

**Verify**: should produce a CSV with 267 rows (or 315 if you don't pre-filter the buried-alive suite — that's fine, just exclude in the selection script).

### Deliverable 2 — Build the scenario set with three tiers

`data/test_eval/maladaptive_scenarios.json` (new). Three tiers in one file with a `tier` field — the existing eval harness already supports this from the integration-eval pilot.

**Selection pool**: Ramon's targeted annotation log at `data/benchmarks/test_annotation_log.json` (109 vetted cases). Cross-reference with `data/benchmarks/spot_check_round2.json` (round 2, 30 stratified cases).

**Per-node vetted-unsafe coverage** (computed during this handoff's prep — verify before you trust):
| Node | r1 spot-check | r2 spot-check | VR-targeted | Total |
|---|---|---|---|---|
| AVOIDANCE | 3 | 3 | 0 | 6 |
| INTERRUPTION | 3 | 3 | 0 | 6 |
| SUPPRESSION | 3 | 3 | 0 | 6 |
| TRAUMA_REPLAY | 3 | 3 | 0 | 6 |
| VIOLENT_REVENGE | 3 | 0 | 16 | 19 |

#### Tier 1: `tier="main"` (headline) — 25 scenarios

5 per unsafe node, drawn from the vetted-unsafe pool above, restricted to:
- `gt_safe=False` per Ramon's annotation
- `gt_node` ∈ {AVOIDANCE, INTERRUPTION, VIOLENT_REVENGE, SUPPRESSION, TRAUMA_REPLAY}
- Critic correctly classifies in `test_benchmark_results_postfix.csv` (`pred_safe=False AND pred_node=gt_node`)
- Diversify by `theme`/`suite` if possible (the test set has 7 themes vs dev's 10 — coverage will be slightly thinner)

For VIOLENT_REVENGE specifically: prefer cases targeting people (more ecologically valid per `test_annotation_log.summary.key_findings`) over cases targeting objects/forces (car, elevator, tsunami). `violent_revenge_cases.cases` in the annotation log has `theme` you can sort by.

#### Tier 2: `tier="multipart"` (supplementary) — 0–8 scenarios likely

Same criterion as the dev pilot: `test_type=multipart` AND segmentation contains an adaptive node AND critic verdict correct. Expected: small pool, probably AV+INT only (matches dev). Document the SUP/TR multipart dataset gap as a continuing finding, not a new bug.

#### Tier 3: `tier="robustness"` (NEW — was not in the pilot) — ~9 scenarios

This is the user's explicit ask: cases the critic **mis**classifies, to test end-to-end behavior when the safety layer is wrong. Three flavors, ~3 each:

- `subtier="false_positive"`: `gt_safe=True` (Ramon-vetted safe) but `pred_safe=False` (critic flags unsafe → constraint fires inappropriately). AFFECT_EXPRESSION (n=18) and boundary (n=36) pools are natural sources — these are the cases where Ramon noted classifier confusion.
- `subtier="false_negative"`: `gt_safe=False` (Ramon-vetted unsafe) but `pred_safe=True` (critic misses → no constraint fires).
- `subtier="wrong_node"`: `gt_safe=False AND pred_safe=False` but `pred_node ≠ gt_node` (critic catches that it's unsafe but picks the wrong pattern → constraint redirects toward the wrong adaptive direction).

Each robustness scenario gets the same A/B treatment. The research question for this tier is *"how does the integrated system behave when the safety layer is wrong?"* — not "does the constraint help."

#### Scenario JSON schema

Same as integration-eval pilot, plus a `subtier` field on robustness rows:
```json
{
  "case_id": "avoidance_01",
  "tier": "main",
  "expected_node": "AVOIDANCE",
  "nightmare": "...",
  "user_input": "...",
  "source_suite": "...",
  "source_test_description": "...",
  "ramon_label": {"safe": false, "node": "AVOIDANCE"},
  "critic_pred": {"safe": false, "node": "AVOIDANCE", "conf": 0.99}
}
```

For robustness rows add `"subtier": "false_positive" | "false_negative" | "wrong_node"`.

### Deliverable 3 — Run the eval pipeline + prepare expert rating sheet

The pipeline scripts already exist. Re-use them with new paths.

```bash
# 1. Generate (~10 min on Scaleway Mistral Small)
uv run python experiments/integration_eval/run_integration_eval.py \
    --scenarios data/test_eval/maladaptive_scenarios.json \
    --output data/test_eval/test_eval_results.csv

# 2. Judge with LLM (supplementary continuity check, not headline) (~10 min on OpenRouter)
uv run python experiments/integration_eval/judge_responses.py \
    --input data/test_eval/test_eval_results.csv

# 3. Summary md
uv run python experiments/integration_eval/summarize_results.py \
    --input data/test_eval/test_eval_results.csv \
    --output data/test_eval/test_eval_summary.md
```

The summarize script currently splits by `tier`. You'll want to extend it to also break out `subtier` for the robustness section — small change in `summarize_results.py`. Add a third sub-table.

**Then export an expert rating sheet.** New script `experiments/integration_eval/export_for_experts.py` that reads `test_eval_results.csv` and produces a clean spreadsheet (CSV/XLSX) with columns:
- `case_id`, `tier`, `condition`, `nightmare`, `user_input`, `response`
- Empty rater columns: `expert_redirect_quality` (strong/partial/absent), `expert_validates_appropriately` (yes/no/n/a), `expert_clinically_acceptable` (yes/no), `expert_notes` (free text)
- **Hide condition (control/treatment) from raters** — randomize row order and use a key file mapping shuffled-row-id → real (case_id, condition). Otherwise rater bias contaminates the comparison.
- Hide `detected_node`, `judge_*` columns.

Two output files: `test_eval_for_experts.xlsx` (or csv) for distribution, and `test_eval_rater_key.json` (kept locally, used to merge expert ratings back into the main CSV).

## Methodology notes

- **The expert rating is the §4.5 headline.** The LLM judge in step 2 is supplementary — useful for (a) checking its judgments correlate with the experts on overlapping items (a rough validation of the pilot's judge), and (b) covering the robustness tier where you may not want to burden experts with all 18 robustness rows.
- **Held-out** = no leakage. Don't re-tune the constraint or any prompt against test-set findings during this eval. If something breaks, document; don't fix-then-re-eval.
- **Sample sizes**: 25 main + ~8 multipart + ~9 robustness ≈ 42 scenarios × 2 conditions ≈ 84 generations. Same harness, same judge, comparable to pilot. Expert annotation burden: ~50 rows for the main+multipart tier (ask experts to skip robustness or rate a sub-sample).
- **Boundary cases (n=36) are documented in `test_annotation_log` as low ecological validity** (templated, GPT-5.4 produces 6 repeating patterns). Don't put them in the headline tier. They can supply false-positive cases for the robustness tier if the critic disagrees with Ramon's labels.
- **AFFECT_EXPRESSION cases (n=18) are noted as low ecological validity** (resemble clinical observation rather than patient rewriting). Same as boundary — fine for robustness sourcing, not for headline.
- **VR object-targeting cases (car, elevator, wave) are noted as less ecologically valid** than person-targeting (surgery). Filter accordingly when picking the 5 VR scenarios.
- **The pilot's two findings should be testable predictions on test data**: if the asymmetric Δ replicates (AV/INT lift, VR/SUP/TR flat-or-regressive), the finding generalizes. If it doesn't, that's also interesting. Don't be surprised by either outcome.

## Rate-limit and timing notes

- Scaleway Mistral Small: response_agent uses it. If a benchmark is running, do not run the eval (same lesson as the pilot). Check `ps aux | grep run_benchmark`.
- OpenRouter (OR_GPT5_4): judge step. Independent of Scaleway.
- Sequence: re-run test benchmark → wait → run scenario selection → run eval → run judge → run summary → export expert sheet.

## Thesis integration

This produces thesis §4.5 — the system-level expert-rated eval. Structure:

1. Method: held-out test set, A/B with synthetic conversation history, three tiers (main / multipart / robustness), two raters (Gieselmann + Lüth) on main+multipart with IRR, LLM judge as supplementary continuity check across all rows.
2. Headline table: Δ on main tier (control vs treatment, expert ratings).
3. Per-node breakdown.
4. Multipart sub-table.
5. Robustness sub-table — qualitative discussion: how does the system behave when the safety layer is wrong? (False positives → does the chatbot push back? False negatives → does the base prompt save the day? Wrong-node → does the redirect still work directionally?)
6. Compare to pilot Δ from §4.4.x — does the asymmetric pattern replicate?
7. Limitations: dataset-gen artifacts (per `test_annotation_log.summary.data_limitations`), small N per cell, single-rater-per-case in robustness tier.

## Don'ts

- **Don't modify the base IRT system.** Same rationale as the pilot — confounds the comparison.
- **Don't modify the safety layer mid-eval.** Tweak A is in. If you find new failure modes, document for future work, don't fix.
- **Don't drop the rater-blinding step on the export.** Letting raters see condition labels would contaminate the headline.
- **Don't re-run the pilot scripts on dev to "improve" them** — the pilot is closed.
- **Don't try to hit a specific Δ.** Even at expert-rating resolution, pp-level shifts on N≈5 are within rater noise. Report what you observe.
- **Don't expand the robustness tier indefinitely.** ~9 cases is the budget. More flavors of misclassification = more rater burden = lower IRR per case.

## Report back when done

```
Phase 4 system-level eval — held-out test set:
- Test benchmark re-run: <cases>, post-fix critic accuracy/recall = X%/Y%
- Scenarios in set: N main + M multipart + K robustness = total
- Eval generation: completed, csv at data/test_eval/test_eval_results.csv
- LLM judge (supplementary): completed, summary at .../test_eval_summary.md
- Pilot finding replication: <yes/partial/no>
  - Main-tier headline Δ: control X% strong / treatment X'% strong (LLM judge)
  - Per-node: AV: ..., INT: ..., VR: ..., SUP: ..., TR: ...
- Robustness tier: <one-line summary per subtier>
- Expert rating sheet: data/test_eval/test_eval_for_experts.xlsx, key at .../test_eval_rater_key.json
- Outstanding before §4.5 numbers can be cited:
  - Send rating sheet to Gieselmann + Lüth
  - Merge expert ratings back via key file
  - IRR computation between Gieselmann + Lüth on overlapping items

Commit SHA: <sha>
```

## Reference files (read if you need depth)

- `docs/planning/HANDOFF_INTEGRATION_EVAL.md` — the pilot handoff this builds on
- `docs/planning/integration_eval_notes.md` — pilot findings + Tweak A pilot results (read both 2026-04-27 addendums)
- `data/integration_eval/maladaptive_scenarios.json` — the pilot's scenario file (structure reference)
- `data/integration_eval/integration_eval_summary.md` — v1 (pilot headline)
- `data/integration_eval/integration_eval_summary_v2.md` — v2 (post-Tweak-A supplementary)
- `data/benchmarks/test_dataset.json` — held-out test set (315 cases, 7 themes; 48 buried-alive excluded)
- `data/benchmarks/test_annotation_log.json` — Ramon's 114-case annotation, including data-quality notes
- `data/benchmarks/spot_check_round2.json` — 30 stratified spot-check cases
- `data/benchmarks/test_benchmark_results.csv` — STALE (pre-fix). Don't trust for selection; re-run as Deliverable 1.
- `safety/critic.py:562` — `_build_constraint_message` (current production, post-Tweak-A)
- `tests/test_constraint_synthesis.py` — 11 smoke tests; should still pass — run before starting to confirm baseline
- `experiments/integration_eval/run_integration_eval.py` — eval harness; re-use with new --scenarios/--output
- `experiments/integration_eval/judge_responses.py` — judge; calibrated rubric committed in 33908f1
- `experiments/integration_eval/summarize_results.py` — summarizer; extend with subtier breakdown
