# Test Benchmark Evaluation — Handoff

## What just happened
The test set benchmark has finished running. Results need to be parsed and analyzed.

## Files
- **Test benchmark results:** `data/benchmarks/test_benchmark_results.csv` (check exact filename — might also be just `benchmark_results.csv` if it overwrote, or a different name if `--output` was used)
- **Test dataset:** `data/benchmarks/test_dataset.json` (315 cases, 7 themes)
- **Annotation log:** `data/benchmarks/test_annotation_log.json` (human-annotated ground truth, 84 cases reviewed)
- **Dev benchmark for comparison:** `data/benchmarks/benchmark_results.csv` (480 cases, post-affect-expression fix)
- **Latest thesis structure:** `docs/planning/thesis_skeleton.md` (Mar 25, 2026)
- **Exposé with evaluation plan:** `docs/planning/Master's Thesis Exposé Claude.md`

## Known data issues
1. **Buried alive suite excluded** — GPT-5.4 content filter truncated nightmare text. 48 cases. Exclude from primary evaluation.
2. **Boundary cases (36 remaining)** — templated, not genuinely ambiguous. Report separately as exploratory, not in primary metrics.
3. **Primary evaluation set:** 231 cases (clean + multipart from 6 valid themes)

## What to analyze
1. Parse test_benchmark_results.csv — compute safety accuracy, unsafe recall, node accuracy (same script pattern as dev)
2. Exclude buried alive suite from primary metrics
3. Report primary (231 clean+multipart) and exploratory (36 boundary) separately
4. Compare to dev set results: dev had 93.8% safety accuracy, 98.9% unsafe recall on clean cases
5. Check AFFECT_EXPRESSION — how many classified as EMOTIONAL_MASTERY at node level? (expected: most)
6. Check VIOLENT_REVENGE — any missed as BEHAVIORAL_MASTERY? (known weak spot)
7. Check the 2 false positive patterns from dev (VIOLENT_REVENGE→BEHAVIORAL_MASTERY)

## Dev set reference numbers (post-affect-expression fix)
- Safety accuracy (clean, 420 cases): 93.8%
- Unsafe recall: 98.9% (2 FPs, both VIOLENT_REVENGE→BEHAVIORAL_MASTERY)
- False negatives (safe→unsafe): 24 (mostly MYTHICAL_MASTERY and EMOTIONAL_MASTERY flagged as TRAUMA_REPLAY — conservative, clinically safe direction)
- Node accuracy: 70.2%

## What comes after
1. Analyze test results (this handoff)
2. Phase 3: Integrate SafetyCritic into AI/irt_app.py
3. Phase 4: System-level evaluation — single-turn, baseline vs KG-augmented, expert-rated by Gieselmann + Katharina Lüth (Osnabrück, IRT researcher)
4. Write thesis (latest structure: docs/planning/thesis_skeleton.md)

## Key memories (in /mnt/.auto-memory/)
- AFFECT_EXPRESSION: pure negative affect restatement = trauma replay, not neutral
- Violent revenge literature: Seebauer 2014, Todorov 2016, Kunze 2025 — not acutely dangerous but therapeutically inferior
- Critic beats generator: critic correctly flagged GPT-5.4 mislabeled AFFECT_EXPRESSION cases
- Meta-narration fix: ban "in the rewrite" phrasing in generation prompt
