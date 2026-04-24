# Pre-fix benchmark CSVs (archive — provenance only)

These CSVs were produced **before** the segmenter determinism fix and use the
non-deterministic OpenRouter aggregator config (`OR_MISTRAL_NEMO`, temperature=0.1)
for the segmenter stage of the safety pipeline.

Do **not** treat these as current thesis-anchoring numbers. They are retained
for provenance and for diff comparison against the post-fix runs.

## Files

| File | Run date | Config | Notes |
|---|---|---|---|
| `benchmark_results.csv` | 2026-04-22 | S1, OR + temp=0.1 segmenter | Re-run S1 baseline used in §10 of System2_CoT_Findings.md |
| `benchmark_results_s1_consistency.csv` | 2026-04-20 → 04-22 | S1 + N=5 semantic consistency, OR segmenter | Showed 6 regressions vs baseline traced to segmenter drift |
| `benchmark_results_s2.csv` | 2026-03-25 | S2 baseline, OR segmenter | Stale — predates the affect-fix dataset regeneration; superseded by post-fix run |
| `benchmark_results_s2_consistency.csv` | 2026-04-20 → 04-22 | S2 + N=5 semantic consistency, OR segmenter | |
| `_test_noconsistency.csv` | 2026-04-22 | Smoke-test artifact | Throwaway baseline for the consistency-vs-baseline diff |

## Why pre-fix runs are not authoritative

The OR aggregator routes Mistral Nemo requests across heterogeneous upstream
backends, producing run-to-run segmentation drift on identical input even at
low temperature. Determinism probe (2026-04-22) showed:

- OR + temp=0.1: 5/6 cases drifted (mean 2.33 unique segment signatures / 5 runs)
- OR + temp=0:   6/6 cases drifted (mean 2.33 unique signatures / 5 runs)
- SW + temp=0.1: 1/6 cases drifted (mean 1.17 unique signatures / 5 runs)
- SW + temp=0:   0/6 cases drifted (mean 1.00 unique signatures / 5 runs)

See `docs/planning/System2_CoT_Findings.md` §10.3.1 for the full diagnosis.

The post-fix segmenter uses the Scaleway-direct Mistral Nemo endpoint at
temperature=0 (greedy decoding), which is fully deterministic on the probe
set. Post-fix benchmarks live at `data/benchmarks/benchmark_results*.csv`.
