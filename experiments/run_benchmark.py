#!/usr/bin/env python3
"""
Benchmark Evaluation Script for Safety Critic

Loads a hierarchical JSON dataset (like contextual_batch_tests.json format),
runs the Safety Critic against every test case, and generates a detailed CSV report.

Usage:
    python run_benchmark.py                              # Uses default dev_dataset.json
    python run_benchmark.py --input data/test_dataset.json
    python run_benchmark.py --input data/dev_dataset.json --output results/benchmark.csv
"""

import os
import sys
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from safety.critic import SafetyCritic


async def run_benchmark(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Run the benchmark evaluation on a dataset.
    
    Args:
        input_file: Path to the JSON dataset file
        output_file: Path to save the CSV results
        
    Returns:
        DataFrame with all results
    """
    
    # Load dataset
    print("=" * 70)
    print("SAFETY CRITIC BENCHMARK EVALUATION")
    print("=" * 70)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print()
    
    print("Loading dataset...")
    with open(input_file, 'r', encoding='utf-8') as f:
        suites = json.load(f)
    
    total_tests = sum(len(suite.get("tests", [])) for suite in suites)
    print(f"✓ Loaded {len(suites)} suites with {total_tests} total tests")
    print()
    
    # Initialize SafetyCritic
    print("Initializing SafetyCritic...")
    critic = SafetyCritic()
    print("✓ SafetyCritic initialized")
    print()
    
    # Run evaluation
    results = []
    start_time = datetime.now()
    test_counter = 0
    
    for suite_idx, suite in enumerate(suites, 1):
        suite_name = suite.get("suite", f"Suite {suite_idx}")
        nightmare = suite.get("nightmare", "")
        tests = suite.get("tests", [])
        
        print(f"Processing Suite {suite_idx}/{len(suites)}: \"{suite_name[:50]}...\"")
        print(f"  Nightmare: \"{nightmare[:60]}...\"")
        print(f"  Tests: {len(tests)}")
        
        for test_idx, test in enumerate(tests, 1):
            test_counter += 1
            description = test.get("description", f"Test {test_idx}")
            user_input = test.get("input", "")
            expected_safe = test.get("expected_safe")
            expected_node = test.get("expected_node")  # May be None
            
            try:
                # Evaluate with nightmare context
                result = await critic.evaluate_intervention(
                    user_input,
                    nightmare_context=nightmare
                )
                
                # Extract results
                predicted_safe = result.is_safe
                predicted_node = result.node_id
                confidence_score = result.confidence
                constraint_text = result.constraint or ""
                
                # Calculate correctness
                is_safety_correct = (predicted_safe == expected_safe) if expected_safe is not None else None
                
                # Node correctness only if expected_node is provided
                if expected_node is not None:
                    is_node_correct = (predicted_node == expected_node)
                else:
                    is_node_correct = None  # NaN in pandas
                
                # Store result
                results.append({
                    "suite_name": suite_name,
                    "nightmare_context": nightmare[:100] + "..." if len(nightmare) > 100 else nightmare,
                    "test_description": description,
                    "user_input": user_input,
                    "ground_truth_safe": expected_safe,
                    "ground_truth_node": expected_node,
                    "predicted_safe": predicted_safe,
                    "predicted_node": predicted_node,
                    "confidence_score": confidence_score,
                    "is_safety_correct": is_safety_correct,
                    "is_node_correct": is_node_correct,
                    "critic_constraint": constraint_text[:500] if constraint_text else "",  # Truncate long constraints
                })
                
                # Brief status indicator
                status = "✓" if is_safety_correct else "✗"
                print(f"    {status} [{test_counter}/{total_tests}] {description}")
                
            except Exception as e:
                print(f"    ✗ [{test_counter}/{total_tests}] {description} - ERROR: {e}")
                results.append({
                    "suite_name": suite_name,
                    "nightmare_context": nightmare[:100] + "..." if len(nightmare) > 100 else nightmare,
                    "test_description": description,
                    "user_input": user_input,
                    "ground_truth_safe": expected_safe,
                    "ground_truth_node": expected_node,
                    "predicted_safe": None,
                    "predicted_node": "ERROR",
                    "confidence_score": None,
                    "is_safety_correct": False,
                    "is_node_correct": False,
                    "critic_constraint": f"ERROR: {str(e)}",
                })
        
        print()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"✓ Results saved to: {output_file}")
    
    # Calculate metrics
    elapsed = datetime.now() - start_time
    
    print()
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(df)}")
    print(f"Time Elapsed: {elapsed}")
    print()
    
    # Safety accuracy
    safety_correct = df["is_safety_correct"].sum()
    safety_total = df["is_safety_correct"].notna().sum()
    safety_accuracy = (safety_correct / safety_total * 100) if safety_total > 0 else 0
    print(f"Safety Accuracy: {safety_correct}/{safety_total} ({safety_accuracy:.1f}%)")
    
    # Node accuracy (only where expected_node was provided)
    node_df = df[df["ground_truth_node"].notna()]
    if len(node_df) > 0:
        node_correct = node_df["is_node_correct"].sum()
        node_total = len(node_df)
        node_accuracy = (node_correct / node_total * 100) if node_total > 0 else 0
        print(f"Node Accuracy (strict): {node_correct}/{node_total} ({node_accuracy:.1f}%)")
    else:
        print("Node Accuracy: N/A (no expected_node labels)")
    
    # Average confidence
    avg_confidence = df["confidence_score"].mean()
    if pd.notna(avg_confidence):
        print(f"Average Confidence: {avg_confidence*100:.1f}%")
    
    print()
    
    # Breakdown by ground truth
    print("Breakdown by Ground Truth:")
    safe_tests = df[df["ground_truth_safe"] == True]
    unsafe_tests = df[df["ground_truth_safe"] == False]
    
    if len(safe_tests) > 0:
        safe_correct = safe_tests["is_safety_correct"].sum()
        print(f"  Safe (expected): {safe_correct}/{len(safe_tests)} correct ({safe_correct/len(safe_tests)*100:.1f}%)")
    
    if len(unsafe_tests) > 0:
        unsafe_correct = unsafe_tests["is_safety_correct"].sum()
        print(f"  Unsafe (expected): {unsafe_correct}/{len(unsafe_tests)} correct ({unsafe_correct/len(unsafe_tests)*100:.1f}%)")
    
    print()
    
    # Breakdown by node type (where applicable)
    if len(node_df) > 0:
        print("Breakdown by Expected Node:")
        for node in node_df["ground_truth_node"].unique():
            node_subset = node_df[node_df["ground_truth_node"] == node]
            correct = node_subset["is_node_correct"].sum()
            total = len(node_subset)
            print(f"  {node}: {correct}/{total} ({correct/total*100:.1f}%)")
    
    print()
    
    # Confusion matrix for safety
    print("Safety Confusion Matrix:")
    print("                    Predicted Safe    Predicted Unsafe")
    
    tp = len(df[(df["ground_truth_safe"] == True) & (df["predicted_safe"] == True)])
    fp = len(df[(df["ground_truth_safe"] == False) & (df["predicted_safe"] == True)])
    tn = len(df[(df["ground_truth_safe"] == False) & (df["predicted_safe"] == False)])
    fn = len(df[(df["ground_truth_safe"] == True) & (df["predicted_safe"] == False)])
    
    print(f"  Actually Safe:    {tp:>10}          {fn:>10}")
    print(f"  Actually Unsafe:  {fp:>10}          {tn:>10}")
    
    # Precision, Recall, F1 for "Unsafe" class (more clinically important)
    print()
    print("Unsafe Detection Metrics (clinically important):")
    precision = tn / (tn + fn) if (tn + fn) > 0 else 0
    recall = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"  Precision (Unsafe): {precision*100:.1f}%")
    print(f"  Recall (Unsafe): {recall*100:.1f}%")
    print(f"  F1 (Unsafe): {f1*100:.1f}%")
    
    print()
    print("=" * 70)
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Run Safety Critic benchmark evaluation on a dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_benchmark.py
    python run_benchmark.py --input data/test_dataset.json
    python run_benchmark.py --input data/dev_dataset.json --output results/dev_results.csv
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='data/dev_dataset.json',
        help="Path to input JSON dataset (default: data/dev_dataset.json)"
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/benchmark_results.csv',
        help="Path to output CSV results (default: data/benchmark_results.csv)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths relative to project root
    project_root = Path(__file__).parent.parent
    input_file = project_root / args.input
    output_file = project_root / args.output
    
    # Check input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        print(f"Available files in data/:")
        data_dir = project_root / "data"
        if data_dir.exists():
            for f in data_dir.iterdir():
                print(f"  - {f.name}")
        sys.exit(1)
    
    # Run benchmark
    asyncio.run(run_benchmark(input_file, output_file))


if __name__ == "__main__":
    main()

