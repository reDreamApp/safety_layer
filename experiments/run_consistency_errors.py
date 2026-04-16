#!/usr/bin/env python3
"""
Targeted Semantic Consistency Run on Error Cases

Runs semantic consistency (N=5, temp=0.7) on just the cases where S1 and/or S2
made safety errors. Quick and cheap (~22 min) — answers the key question:
does voting disagreement predict errors better than logprobs?

Also runs on a matched sample of correct cases for comparison.

Usage:
    uv run python experiments/run_consistency_errors.py
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from safety.classifier import ClinicalClassifier, NODE_TO_CODE
from safety.classifier_cot import ClinicalClassifierCoT
from safety.semantic_consistency import evaluate_semantic_consistency


def load_error_cases(benchmark_csv: Path, dataset_json: Path) -> list:
    """
    Extract the test cases that were safety errors from a benchmark CSV,
    matched back to the original dataset (to get nightmare context).
    """
    df = pd.read_csv(benchmark_csv)
    errors = df[df["safe_ok"] == False]

    # Load full dataset for nightmare context
    with open(dataset_json, "r") as f:
        suites = json.load(f)

    # Build lookup: (suite_short, test_description) -> nightmare context
    suite_lookup = {}
    for suite in suites:
        suite_name = suite.get("suite", "")
        # The benchmark truncates suite names to 40 chars + "..."
        suite_short = suite_name[:40] + "..." if len(suite_name) > 40 else suite_name
        for test in suite.get("tests", []):
            key = (suite_short, test.get("description", ""))
            suite_lookup[key] = {
                "nightmare": suite.get("nightmare", ""),
                "input": test.get("input", ""),
                "expected_safe": test.get("expected_safe"),
                "expected_node": test.get("expected_node"),
                "description": test.get("description", ""),
            }

    cases = []
    for _, row in errors.iterrows():
        key = (row["suite"], row["test"])
        if key in suite_lookup:
            case = suite_lookup[key].copy()
            case["pred_node"] = row["pred_node"]
            case["conf"] = row["conf"]
            cases.append(case)
        else:
            # Fallback: use data from CSV directly
            cases.append({
                "nightmare": "",
                "input": row["user_input"],
                "expected_safe": row["gt_safe"],
                "expected_node": row["gt_node"],
                "description": row["test"],
                "pred_node": row["pred_node"],
                "conf": row["conf"],
            })

    return cases


def load_correct_sample(benchmark_csv: Path, dataset_json: Path, n_sample: int = 25) -> list:
    """
    Load a matched sample of correct predictions for comparison.
    Stratified: pick from different confidence buckets.
    """
    df = pd.read_csv(benchmark_csv)
    correct = df[df["safe_ok"] == True].copy()

    # Stratify by confidence — pick some high, some medium-low
    correct = correct.sort_values("conf")
    # Take bottom 10 (lowest confidence correct), top 5, and 10 random from middle
    bottom = correct.head(10)
    top = correct.tail(5)
    middle = correct.iloc[10:-5].sample(n=min(10, len(correct) - 15), random_state=42)
    sample = pd.concat([bottom, middle, top])

    # Load dataset for context — build lookup by input text (first 100 chars)
    # to handle mismatched test descriptions between benchmark runs
    with open(dataset_json, "r") as f:
        suites = json.load(f)

    input_lookup = {}
    for suite in suites:
        nightmare = suite.get("nightmare", "")
        for test in suite.get("tests", []):
            key = test.get("input", "")[:100].strip()
            input_lookup[key] = {
                "nightmare": nightmare,
                "input": test.get("input", ""),
                "expected_safe": test.get("expected_safe"),
                "expected_node": test.get("expected_node"),
                "description": test.get("description", ""),
            }

    cases = []
    for _, row in sample.iterrows():
        # Match on user_input text (robust to description mismatches)
        key = row["user_input"][:100].strip()
        if key in input_lookup:
            case = input_lookup[key].copy()
            case["pred_node"] = row["pred_node"]
            case["conf"] = row["conf"]
            cases.append(case)
        else:
            # Fallback: use data from CSV directly (no nightmare context)
            cases.append({
                "nightmare": "",
                "input": row["user_input"],
                "expected_safe": row["gt_safe"],
                "expected_node": row["gt_node"],
                "description": row["test"],
                "pred_node": row["pred_node"],
                "conf": row["conf"],
            })

    return cases


async def run_consistency_on_cases(
    classifier,
    cases: list,
    label: str,
    n_runs: int = 5,
) -> list:
    """Run semantic consistency on a list of cases."""
    results = []

    for i, case in enumerate(cases, 1):
        desc = case["description"]
        user_input = case["input"]
        context = case.get("nightmare") or None

        print(f"  [{i}/{len(cases)}] {desc}...")

        result = await evaluate_semantic_consistency(
            classifier=classifier,
            user_text=user_input,
            context=context,
            n_runs=n_runs,
            stochastic_temperature=0.7,
            confidence_threshold=0.8,
        )

        # Get deterministic logprobs confidence
        det_conf = None
        det_node = None
        if result.deterministic_result:
            det_conf = result.deterministic_result.confidence
            det_node = result.deterministic_result.node_id

        results.append({
            "system": label,
            "description": desc,
            "input": user_input[:80],
            "gt_safe": case.get("expected_safe"),
            "gt_node": case.get("expected_node"),
            "det_node": det_node or result.node_id,
            "det_conf": det_conf,
            "consistency_node": result.node_id,
            "consistency_code": result.code,
            "agreement": result.agreement_ratio,
            "is_confident": result.is_confident,
            "votes": json.dumps(result.vote_distribution),
            "n_runs": result.n_runs,
            "original_pred": case.get("pred_node", ""),
            "original_conf": case.get("conf"),
            # Computational cost (total across 1 deterministic + N stochastic)
            "input_tokens": result.total_input_tokens,
            "output_tokens": result.total_output_tokens,
            "latency_ms": round(result.total_latency_ms, 1),
        })

        agreement_str = f"{result.agreement_ratio:.0%}"
        latency_s = result.total_latency_ms / 1000
        print(f"         -> {result.code} (agreement={agreement_str}, {latency_s:.1f}s, {result.total_input_tokens}+{result.total_output_tokens} tok)")

    return results


async def main():
    project_root = Path(__file__).parent.parent
    dataset_path = project_root / "data" / "benchmarks" / "dev_dataset.json"
    s1_csv = project_root / "data" / "benchmarks" / "benchmark_results.csv"
    s2_csv = project_root / "data" / "benchmarks" / "benchmark_results_s2.csv"

    print("=" * 70)
    print("TARGETED SEMANTIC CONSISTENCY: Error Cases")
    print("=" * 70)

    # Load error cases
    s1_errors = load_error_cases(s1_csv, dataset_path)
    s2_errors = load_error_cases(s2_csv, dataset_path)
    # Also load a sample of correct cases for comparison
    s1_correct_sample = load_correct_sample(s1_csv, dataset_path, n_sample=25)
    s2_correct_sample = load_correct_sample(s2_csv, dataset_path, n_sample=25)

    print(f"S1 error cases: {len(s1_errors)}")
    print(f"S2 error cases: {len(s2_errors)}")
    print(f"S1 correct sample: {len(s1_correct_sample)}")
    print(f"S2 correct sample: {len(s2_correct_sample)}")

    # Deduplicate: some cases may be errors in both systems
    all_cases_set = set()
    for c in s1_errors + s2_errors:
        all_cases_set.add(c["input"])
    print(f"Unique cases to evaluate: {len(all_cases_set)} errors + ~50 correct controls")
    print()

    # Initialize classifiers
    s1 = ClinicalClassifier()
    s2 = ClinicalClassifierCoT()

    all_results = []
    start_time = datetime.now()

    # Run S1 on its error cases
    print(f"\n--- S1 Errors ({len(s1_errors)} cases) ---")
    s1_err_results = await run_consistency_on_cases(s1, s1_errors, "S1_error")
    all_results.extend(s1_err_results)

    # Run S1 on correct sample
    print(f"\n--- S1 Correct Sample ({len(s1_correct_sample)} cases) ---")
    s1_cor_results = await run_consistency_on_cases(s1, s1_correct_sample, "S1_correct")
    all_results.extend(s1_cor_results)

    # Run S2 on its error cases
    print(f"\n--- S2 Errors ({len(s2_errors)} cases) ---")
    s2_err_results = await run_consistency_on_cases(s2, s2_errors, "S2_error")
    all_results.extend(s2_err_results)

    # Run S2 on correct sample
    print(f"\n--- S2 Correct Sample ({len(s2_correct_sample)} cases) ---")
    s2_cor_results = await run_consistency_on_cases(s2, s2_correct_sample, "S2_correct")
    all_results.extend(s2_cor_results)

    elapsed = datetime.now() - start_time

    # Save results
    df = pd.DataFrame(all_results)
    output_path = project_root / "data" / "benchmarks" / f"consistency_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to: {output_path}")

    # Summary
    print(f"\nTime elapsed: {elapsed}")
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for group in ["S1_error", "S1_correct", "S2_error", "S2_correct"]:
        gdf = df[df["system"] == group]
        if len(gdf) == 0:
            continue
        avg_agree = gdf["agreement"].mean()
        n_confident = gdf["is_confident"].sum()
        n_total = len(gdf)
        avg_logprobs = gdf["det_conf"].mean() if gdf["det_conf"].notna().any() else 0

        print(f"\n  {group} ({n_total} cases):")
        print(f"    Avg agreement:     {avg_agree:.0%}")
        print(f"    Confident (≥80%):  {n_confident}/{n_total}")
        print(f"    Avg logprobs conf: {avg_logprobs:.3f}")

    # The key question: is agreement lower on error cases than correct cases?
    for sys_prefix in ["S1", "S2"]:
        err_df = df[df["system"] == f"{sys_prefix}_error"]
        cor_df = df[df["system"] == f"{sys_prefix}_correct"]
        if len(err_df) > 0 and len(cor_df) > 0:
            err_agree = err_df["agreement"].mean()
            cor_agree = cor_df["agreement"].mean()
            separation = cor_agree - err_agree
            print(f"\n  {sys_prefix} Separation (correct - error agreement): {separation:.3f}")
            print(f"    Error avg agreement:   {err_agree:.3f}")
            print(f"    Correct avg agreement: {cor_agree:.3f}")
            if separation > 0.05:
                print(f"    → Semantic consistency DOES distinguish errors from correct ({separation:.0%} gap)")
            else:
                print(f"    → Semantic consistency does NOT clearly distinguish errors ({separation:.0%} gap)")


if __name__ == "__main__":
    asyncio.run(main())
