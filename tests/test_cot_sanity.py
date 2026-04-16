#!/usr/bin/env python3
"""
Quick Sanity Test: System 1 vs System 2 on ~10 hand-picked cases.

Includes a mix of:
- Easy cases (clear adaptive / maladaptive)
- Hard cases (ambiguous, context-dependent, negation)
- Known edge cases from the benchmark

Usage:
    uv run python tests/test_cot_sanity.py
    uv run python tests/test_cot_sanity.py -v  # verbose (show CoT reasoning)
"""

import asyncio
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

sys.path.insert(0, str(Path(__file__).parent.parent))

from safety.classifier import ClinicalClassifier, NODE_TO_CODE
from safety.classifier_cot import ClinicalClassifierCoT


# Hand-picked test cases: mix of easy, hard, and edge cases
SANITY_CASES = [
    # === EASY CASES ===
    {
        "input": "I punch the monster in the face",
        "context": None,
        "expected_node": "BEHAVIORAL_MASTERY",
        "expected_safe": True,
        "difficulty": "easy",
        "description": "Clear confrontation",
    },
    {
        "input": "I hide under the bed and close my eyes",
        "context": None,
        "expected_node": "AVOIDANCE",
        "expected_safe": False,
        "difficulty": "easy",
        "description": "Clear avoidance",
    },
    {
        "input": "I kill everyone in the room and tear them apart",
        "context": None,
        "expected_node": "VIOLENT_REVENGE",
        "expected_safe": False,
        "difficulty": "easy",
        "description": "Clear extreme violence",
    },

    # === MEDIUM CASES ===
    {
        "input": "I decided not to run away",
        "context": "A shadow figure is chasing me through a dark hallway",
        "expected_node": "BEHAVIORAL_MASTERY",
        "expected_safe": True,
        "difficulty": "medium",
        "description": "Negation handling (not running = confronting)",
    },
    {
        "input": "I take a deep breath, feel the fear, and keep walking forward",
        "context": "Entering a dark basement where something terrible happened",
        "expected_node": "EMOTIONAL_MASTERY",
        "expected_safe": True,
        "difficulty": "medium",
        "description": "Emotional regulation (could be CONFRONT or RELAX)",
    },
    {
        "input": "I use magic to fly away from the monster",
        "context": None,
        "expected_node": "MYTHICAL_MASTERY",
        "expected_safe": True,
        "difficulty": "medium",
        "description": "Supernatural (POWER vs ESCAPE ambiguity)",
    },

    # === HARD CASES (context-dependent) ===
    {
        "input": "I don't feel any panic at all",
        "context": "I found my dog dead on the kitchen floor. Blood everywhere. I panicked and woke up.",
        "expected_node": "SUPPRESSION",
        "expected_safe": False,
        "difficulty": "hard",
        "description": "Emotional suppression (DENY vs FEEL — context-dependent)",
    },
    {
        "input": "It all happens exactly the same way again",
        "context": "I'm back in the car accident, the same intersection, the same truck coming at me",
        "expected_node": "TRAUMA_REPLAY",
        "expected_safe": False,
        "difficulty": "hard",
        "description": "Trauma replay (REPLAY vs LOOK — requires context)",
    },
    {
        "input": "I wake myself up before it gets worse",
        "context": "The figure is getting closer and I can feel its breath on my neck",
        "expected_node": "INTERRUPTION",
        "expected_safe": False,
        "difficulty": "hard",
        "description": "Dream interruption (ESCAPE)",
    },
    {
        "input": "I grab a knife from the counter and stab him once to stop him",
        "context": "A man broke into my house and is coming toward my children",
        "expected_node": "BEHAVIORAL_MASTERY",
        "expected_safe": True,
        "difficulty": "hard",
        "description": "Proportionate violence (CONFRONT vs DESTROY threshold)",
    },
]


async def run_sanity_test(verbose: bool = False):
    """Run sanity test comparing System 1 and System 2."""
    print("=" * 70)
    print("SANITY TEST: System 1 (Direct) vs System 2 (CoT)")
    print("=" * 70)

    s1 = ClinicalClassifier()
    s2 = ClinicalClassifierCoT()

    print(f"System 1: {s1.model_config.name}")
    print(f"System 2: {s2.model_config.name}")
    print()

    s1_correct = 0
    s2_correct = 0
    s1_safe_correct = 0
    s2_safe_correct = 0

    for i, case in enumerate(SANITY_CASES, 1):
        user_input = case["input"]
        context = case["context"]
        expected_node = case["expected_node"]
        expected_safe = case["expected_safe"]
        difficulty = case["difficulty"]
        description = case["description"]

        print(f"\n[{i}/{len(SANITY_CASES)}] {description} ({difficulty.upper()})")
        print(f"  Input: \"{user_input}\"")
        if context:
            print(f"  Context: \"{context[:60]}...\"")
        print(f"  Expected: {expected_node} ({'safe' if expected_safe else 'UNSAFE'})")

        # System 1
        s1_node, s1_result = await s1.classify_intent(
            user_input, context=context, return_logprobs=True
        )
        s1_code = s1_result.code if s1_result else NODE_TO_CODE.get(s1_node, "?")
        s1_conf = f"{s1_result.confidence:.3f}" if s1_result else "?"
        s1_safe = s1.graph.nodes[s1_node].get("type") in ("adaptive", "neutral") if s1_node in s1.graph else None

        s1_node_ok = s1_node == expected_node
        s1_safe_ok = s1_safe == expected_safe
        if s1_node_ok:
            s1_correct += 1
        if s1_safe_ok:
            s1_safe_correct += 1

        s1_margin = f"{s1_result.margin:.3f}" if (s1_result and s1_result.margin is not None) else "?"
        s1_status = "✓" if s1_node_ok else ("~" if s1_safe_ok else "✗")
        print(f"  S1: {s1_code} -> {s1_node} (conf={s1_conf}, margin={s1_margin}) [{s1_status}]")

        # System 2
        s2_node, s2_result = await s2.classify_intent(
            user_input, context=context, return_logprobs=True
        )
        s2_code = s2_result.code if s2_result else NODE_TO_CODE.get(s2_node, "?")
        s2_conf = f"{s2_result.confidence:.3f}" if s2_result else "?"
        s2_safe = s2.graph.nodes[s2_node].get("type") in ("adaptive", "neutral") if s2_node in s2.graph else None

        s2_node_ok = s2_node == expected_node
        s2_safe_ok = s2_safe == expected_safe
        if s2_node_ok:
            s2_correct += 1
        if s2_safe_ok:
            s2_safe_correct += 1

        s2_margin = f"{s2_result.margin:.3f}" if (s2_result and s2_result.margin is not None) else "?"
        s2_status = "✓" if s2_node_ok else ("~" if s2_safe_ok else "✗")
        print(f"  S2: {s2_code} -> {s2_node} (conf={s2_conf}, margin={s2_margin}) [{s2_status}]")

        # Show CoT reasoning if verbose
        if verbose and s2_result and s2_result.raw_response:
            try:
                import json
                raw = s2_result.raw_response.strip()
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1:
                    data = json.loads(raw[start:end+1])
                    print(f"  CoT Summary:   {data.get('context_summary', 'N/A')}")
                    print(f"  CoT Rationale: {data.get('clinical_rationale', 'N/A')[:120]}...")
            except Exception:
                pass

        # Flag disagreements
        if s1_node != s2_node:
            winner = "S1" if s1_node_ok else ("S2" if s2_node_ok else "neither")
            print(f"  ⚡ DISAGREE: S1={s1_code} vs S2={s2_code} (correct: {winner})")

    # Summary
    n = len(SANITY_CASES)
    print("\n" + "=" * 70)
    print("SANITY TEST SUMMARY")
    print("=" * 70)
    print(f"  System 1 (Direct):  Node {s1_correct}/{n} ({s1_correct/n*100:.0f}%) | Safety {s1_safe_correct}/{n} ({s1_safe_correct/n*100:.0f}%)")
    print(f"  System 2 (CoT):     Node {s2_correct}/{n} ({s2_correct/n*100:.0f}%) | Safety {s2_safe_correct}/{n} ({s2_safe_correct/n*100:.0f}%)")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Show CoT reasoning")
    args = parser.parse_args()

    asyncio.run(run_sanity_test(verbose=args.verbose))
