#!/usr/bin/env python3
"""
System 1 vs System 2 Comparison Benchmark

Runs both classifier variants on the same dataset and compares:
- Classification accuracy (safety + node-level)
- Confidence calibration (logprobs)
- Semantic consistency (optional, N=5 stochastic runs)

Modes:
  --mode logprobs       Run both classifiers with logprobs confidence (default)
  --mode consistency    Run both classifiers with semantic consistency (5x slower)
  --mode both           Run all four combinations

Usage:
    python experiments/run_comparison.py
    python experiments/run_comparison.py --input data/benchmarks/dev_dataset.json --limit 2
    python experiments/run_comparison.py --mode consistency --limit 1
"""

import os
import sys
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from safety.classifier import ClinicalClassifier, ClassificationResult, CODE_MAP, NODE_TO_CODE
from safety.classifier_cot import ClinicalClassifierCoT
from safety.semantic_consistency import evaluate_semantic_consistency


async def classify_single(
    classifier,
    user_input: str,
    nightmare_context: Optional[str] = None,
    system_label: str = "S1",
) -> dict:
    """Run a single classification and return a result dict."""
    try:
        node_id, result = await classifier.classify_intent(
            user_input,
            context=nightmare_context,
            return_logprobs=True,
        )

        # Determine safety from graph
        if node_id in classifier.graph:
            node_type = classifier.graph.nodes[node_id].get("type", "unknown")
        else:
            node_type = "unknown"

        is_safe = node_type in ("adaptive", "neutral")

        return {
            "system": system_label,
            "pred_node": node_id,
            "pred_safe": is_safe,
            "pred_code": result.code if result else NODE_TO_CODE.get(node_id, "?"),
            "confidence": result.confidence if result else None,
            "mean_logprob": result.mean_logprob if result else None,
            "margin": result.margin if result else None,
            "raw_response": (result.raw_response[:200] if result else "")
        }
    except Exception as e:
        return {
            "system": system_label,
            "pred_node": "ERROR",
            "pred_safe": None,
            "pred_code": "ERROR",
            "confidence": None,
            "mean_logprob": None,
            "margin": None,
            "raw_response": str(e)[:200],
        }


async def classify_with_consistency(
    classifier,
    user_input: str,
    nightmare_context: Optional[str] = None,
    system_label: str = "S1",
    n_runs: int = 5,
) -> dict:
    """Run semantic consistency evaluation and return a result dict."""
    try:
        result = await evaluate_semantic_consistency(
            classifier=classifier,
            user_text=user_input,
            context=nightmare_context,
            n_runs=n_runs,
            stochastic_temperature=0.7,
            confidence_threshold=0.8,
        )

        # Determine safety from graph
        node_id = result.node_id
        if node_id in classifier.graph:
            node_type = classifier.graph.nodes[node_id].get("type", "unknown")
        else:
            node_type = "unknown"

        is_safe = node_type in ("adaptive", "neutral")

        # Also get the deterministic logprobs confidence for comparison
        det_confidence = None
        if result.deterministic_result:
            det_confidence = result.deterministic_result.confidence

        return {
            "system": system_label,
            "pred_node": node_id,
            "pred_safe": is_safe,
            "pred_code": result.code,
            "logprobs_confidence": det_confidence,
            "consistency_agreement": result.agreement_ratio,
            "consistency_confident": result.is_confident,
            "vote_distribution": json.dumps(result.vote_distribution),
            "n_runs": result.n_runs,
        }
    except Exception as e:
        return {
            "system": system_label,
            "pred_node": "ERROR",
            "pred_safe": None,
            "pred_code": "ERROR",
            "logprobs_confidence": None,
            "consistency_agreement": None,
            "consistency_confident": None,
            "vote_distribution": "{}",
            "n_runs": 0,
        }


async def run_logprobs_comparison(
    s1_classifier: ClinicalClassifier,
    s2_classifier: ClinicalClassifierCoT,
    suites: List[dict],
    output_file: Path,
) -> pd.DataFrame:
    """Run logprobs-based comparison of System 1 vs System 2."""
    print("\n" + "=" * 70)
    print("MODE: Logprobs Confidence Comparison")
    print("=" * 70)

    results = []
    total_tests = sum(len(s.get("tests", [])) for s in suites)
    counter = 0

    for suite_idx, suite in enumerate(suites, 1):
        suite_name = suite.get("suite", f"Suite {suite_idx}")
        nightmare = suite.get("nightmare", "")
        tests = suite.get("tests", [])

        print(f"\nSuite {suite_idx}/{len(suites)}: \"{suite_name[:50]}...\"")

        for test in tests:
            counter += 1
            description = test.get("description", "")
            user_input = test.get("input", "")
            expected_safe = test.get("expected_safe")
            expected_node = test.get("expected_node")

            # Run both classifiers
            s1_result = await classify_single(
                s1_classifier, user_input, nightmare, "S1_logprobs"
            )
            s2_result = await classify_single(
                s2_classifier, user_input, nightmare, "S2_logprobs"
            )

            for r in [s1_result, s2_result]:
                row = {
                    "suite": suite_name[:40],
                    "test": description,
                    "input": user_input,
                    "gt_safe": expected_safe,
                    "gt_node": expected_node,
                    **r,
                    "safe_ok": (r["pred_safe"] == expected_safe) if expected_safe is not None else None,
                    "node_ok": (r["pred_node"] == expected_node) if expected_node is not None else None,
                }
                results.append(row)

            # Status indicator
            s1_ok = "✓" if s1_result["pred_safe"] == expected_safe else "✗"
            s2_ok = "✓" if s2_result["pred_safe"] == expected_safe else "✗"
            print(
                f"  [{counter}/{total_tests}] {description}: "
                f"S1={s1_result['pred_code']}({s1_ok}) "
                f"S2={s2_result['pred_code']}({s2_ok})"
            )

    df = pd.DataFrame(results)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to {output_file}")
    return df


async def run_consistency_comparison(
    s1_classifier: ClinicalClassifier,
    s2_classifier: ClinicalClassifierCoT,
    suites: List[dict],
    output_file: Path,
    n_runs: int = 5,
) -> pd.DataFrame:
    """Run semantic consistency comparison of System 1 vs System 2."""
    print("\n" + "=" * 70)
    print(f"MODE: Semantic Consistency Comparison (N={n_runs})")
    print("=" * 70)

    results = []
    total_tests = sum(len(s.get("tests", [])) for s in suites)
    counter = 0

    for suite_idx, suite in enumerate(suites, 1):
        suite_name = suite.get("suite", f"Suite {suite_idx}")
        nightmare = suite.get("nightmare", "")
        tests = suite.get("tests", [])

        print(f"\nSuite {suite_idx}/{len(suites)}: \"{suite_name[:50]}...\"")

        for test in tests:
            counter += 1
            description = test.get("description", "")
            user_input = test.get("input", "")
            expected_safe = test.get("expected_safe")
            expected_node = test.get("expected_node")

            # Run both classifiers with consistency
            s1_result = await classify_with_consistency(
                s1_classifier, user_input, nightmare, "S1_consistency", n_runs
            )
            s2_result = await classify_with_consistency(
                s2_classifier, user_input, nightmare, "S2_consistency", n_runs
            )

            for r in [s1_result, s2_result]:
                row = {
                    "suite": suite_name[:40],
                    "test": description,
                    "input": user_input,
                    "gt_safe": expected_safe,
                    "gt_node": expected_node,
                    **r,
                    "safe_ok": (r["pred_safe"] == expected_safe) if expected_safe is not None else None,
                    "node_ok": (r["pred_node"] == expected_node) if expected_node is not None else None,
                }
                results.append(row)

            s1_agree = s1_result.get("consistency_agreement", 0)
            s2_agree = s2_result.get("consistency_agreement", 0)
            print(
                f"  [{counter}/{total_tests}] {description}: "
                f"S1={s1_result['pred_code']}({s1_agree:.0%}) "
                f"S2={s2_result['pred_code']}({s2_agree:.0%})"
            )

    df = pd.DataFrame(results)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to {output_file}")
    return df


def print_summary(df: pd.DataFrame, mode: str):
    """Print comparison summary statistics."""
    print("\n" + "=" * 70)
    print(f"COMPARISON SUMMARY ({mode})")
    print("=" * 70)

    for system in df["system"].unique():
        sdf = df[df["system"] == system]
        total = len(sdf)
        safety_ok = sdf["safe_ok"].sum()
        safety_total = sdf["safe_ok"].notna().sum()
        safety_acc = (safety_ok / safety_total * 100) if safety_total > 0 else 0

        node_df = sdf[sdf["gt_node"].notna()]
        node_ok = node_df["node_ok"].sum() if len(node_df) > 0 else 0
        node_total = len(node_df)
        node_acc = (node_ok / node_total * 100) if node_total > 0 else 0

        print(f"\n  {system}:")
        print(f"    Safety Accuracy: {safety_ok}/{safety_total} ({safety_acc:.1f}%)")
        if node_total > 0:
            print(f"    Node Accuracy:   {node_ok}/{node_total} ({node_acc:.1f}%)")

        # Confidence stats
        if "confidence" in sdf.columns:
            avg_conf = sdf["confidence"].mean()
            if pd.notna(avg_conf):
                print(f"    Avg Confidence (logprobs): {avg_conf:.3f}")

        # Margin of Victory stats
        if "margin" in sdf.columns:
            margin_series = sdf["margin"].dropna()
            if len(margin_series) > 0:
                avg_margin = margin_series.mean()
                min_margin = margin_series.min()
                print(f"    Avg Margin of Victory: {avg_margin:.3f} (min: {min_margin:.3f})")

        if "consistency_agreement" in sdf.columns:
            avg_agree = sdf["consistency_agreement"].mean()
            if pd.notna(avg_agree):
                print(f"    Avg Agreement (consistency): {avg_agree:.0%}")
                n_confident = sdf["consistency_confident"].sum()
                print(f"    Confident (≥80%): {n_confident}/{total}")

        # Unsafe detection
        unsafe_tests = sdf[sdf["gt_safe"] == False]
        if len(unsafe_tests) > 0:
            unsafe_detected = unsafe_tests["safe_ok"].sum()
            recall = unsafe_detected / len(unsafe_tests) * 100
            print(f"    Unsafe Recall: {unsafe_detected}/{len(unsafe_tests)} ({recall:.1f}%)")

    # Disagreement analysis
    if "S1" in df["system"].iloc[0]:
        # Find cases where S1 and S2 disagree
        s1_df = df[df["system"].str.startswith("S1")].reset_index(drop=True)
        s2_df = df[df["system"].str.startswith("S2")].reset_index(drop=True)

        if len(s1_df) == len(s2_df):
            disagree_mask = s1_df["pred_node"].values != s2_df["pred_node"].values
            n_disagree = disagree_mask.sum()
            print(f"\n  Disagreements: {n_disagree}/{len(s1_df)} ({n_disagree/len(s1_df)*100:.1f}%)")

            if n_disagree > 0:
                print("\n  Disagreement cases:")
                for idx in range(len(s1_df)):
                    if disagree_mask[idx]:
                        test = s1_df.iloc[idx]["test"]
                        s1_pred = s1_df.iloc[idx]["pred_code"]
                        s2_pred = s2_df.iloc[idx]["pred_code"]
                        gt = s1_df.iloc[idx]["gt_node"]
                        s1_correct = "✓" if s1_df.iloc[idx]["node_ok"] else "✗"
                        s2_correct = "✓" if s2_df.iloc[idx]["node_ok"] else "✗"
                        print(f"    {test}: S1={s1_pred}{s1_correct} S2={s2_pred}{s2_correct} (gt={gt})")


async def main():
    parser = argparse.ArgumentParser(
        description="Compare System 1 (Direct) vs System 2 (CoT) classifiers."
    )
    parser.add_argument(
        "--input", type=str,
        default="data/benchmarks/dev_dataset.json",
        help="Path to benchmark dataset"
    )
    parser.add_argument(
        "--output-dir", type=str,
        default="data/benchmarks",
        help="Directory for output CSVs"
    )
    parser.add_argument(
        "--mode", type=str,
        choices=["logprobs", "consistency", "both"],
        default="logprobs",
        help="Comparison mode (default: logprobs)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit to first N suites"
    )
    parser.add_argument(
        "--n-runs", type=int, default=5,
        help="Stochastic runs for consistency mode (default: 5)"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    input_file = project_root / args.input
    output_dir = project_root / args.output_dir

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # Load dataset
    with open(input_file, "r", encoding="utf-8") as f:
        suites = json.load(f)

    if args.limit:
        suites = suites[:args.limit]

    total_tests = sum(len(s.get("tests", [])) for s in suites)
    print("=" * 70)
    print("SYSTEM 1 vs SYSTEM 2 COMPARISON")
    print("=" * 70)
    print(f"Dataset: {input_file.name}")
    print(f"Suites: {len(suites)}, Tests: {total_tests}")
    print(f"Mode: {args.mode}")

    # Initialize classifiers
    print("\nInitializing classifiers...")
    s1 = ClinicalClassifier()
    s2 = ClinicalClassifierCoT()
    print(f"  System 1 (Direct): {s1.model_config.name}")
    print(f"  System 2 (CoT):    {s2.model_config.name}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.mode in ("logprobs", "both"):
        output_file = output_dir / f"comparison_logprobs_{timestamp}.csv"
        df = await run_logprobs_comparison(s1, s2, suites, output_file)
        print_summary(df, "logprobs")

    if args.mode in ("consistency", "both"):
        output_file = output_dir / f"comparison_consistency_{timestamp}.csv"
        df = await run_consistency_comparison(
            s1, s2, suites, output_file, n_runs=args.n_runs
        )
        print_summary(df, "consistency")


if __name__ == "__main__":
    asyncio.run(main())
