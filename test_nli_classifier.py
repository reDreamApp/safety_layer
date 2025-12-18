#!/usr/bin/env python3
"""
Test script for NLI-Based Clinical Classifier

Focuses on context-aware classification tests with detailed confidence analysis.
Shows relative confidence as percentage distribution across all labels.
"""

import asyncio
import sys
import numpy as np
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())


def softmax(x):
    """Convert scores to probability distribution."""
    exp_x = np.exp(x - np.max(x))  # Subtract max for numerical stability
    return exp_x / exp_x.sum()


async def test_context_aware_classification():
    """
    Test context-aware classification with detailed confidence analysis.
    
    Shows how the same action can be classified differently based on context,
    and displays confidence as a percentage distribution across all labels.
    """
    print("\n" + "=" * 80)
    print("NLI Context-Aware Classification Tests")
    print("=" * 80)
    
    from safety.classifier import ClinicalClassifier
    
    classifier = ClinicalClassifier()
    
    print(f"\nModel: {classifier.model_name}")
    print(f"Number of hypotheses: {len(classifier.node_hypotheses)}")
    print("\nHypotheses loaded:")
    for node_id, hypothesis in classifier.node_hypotheses.items():
        node_type = classifier.get_node_info(node_id).get("type", "unknown")
        type_emoji = {"adaptive": "✅", "maladaptive": "⚠️", "neutral": "🟡"}.get(node_type, "❓")
        print(f"  {type_emoji} {node_id}: \"{hypothesis}\"")
    
    # Context-aware test cases
    # Format: (action, context, expected_node, description)
    test_cases = [
        # === BEHAVIORAL RESPONSES ===
        ("I fight back", "being attacked by a monster", "BEHAVIORAL_MASTERY", 
         "Fighting when attacked = adaptive action"),
        
        ("I run away", "being chased by a threat", "BEHAVIORAL_MASTERY", 
         "Running from chase = purposeful action"),
        
        ("I punch it", "confronting an attacker", "BEHAVIORAL_MASTERY",
         "Punching attacker = fighting back"),
        
        # === AVOIDANCE BEHAVIORS ===
        ("I hide", "monster searching for me", "ZDPCS_SAFETY_PRINCIPLE",
         "Hiding from threat = avoidance"),
        
        ("I freeze", "predator approaching", "ZDPCS_SAFETY_PRINCIPLE",
         "Freezing = passive avoidance"),
        
        ("I do nothing", "danger all around me", "ZDPCS_SAFETY_PRINCIPLE",
         "Doing nothing = avoidance"),
        
        # === ESCAPE BEHAVIORS ===
        ("I wake myself up", "nightmare becoming too intense", "ZDPCS_INTERRUPT",
         "Waking up = dream escape"),
        
        ("I force the dream to end", "being overwhelmed", "ZDPCS_INTERRUPT",
         "Ending dream = interrupt"),
        
        # === VIOLENCE ===
        ("I kill everyone", "surrounded by enemies", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Killing everyone = excessive violence"),
        
        ("I destroy everything", "trapped in a room", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Destroying everything = chaotic violence"),
        
        # === SOCIAL SUPPORT ===
        ("I call for help", "facing the threat alone", "SOCIAL_MASTERY",
         "Calling for help = seeking support"),
        
        ("I ask my friend to help", "confronting danger together", "SOCIAL_MASTERY",
         "Asking friend = social support"),
        
        # === ENVIRONMENTAL CHANGES ===
        ("I find a weapon", "needing to defend myself", "ENVIRONMENTAL_MASTERY",
         "Finding weapon = environmental resource"),
        
        ("I discover a safe room", "escaping the threat", "ENVIRONMENTAL_MASTERY",
         "Finding safe place = environmental change"),
        
        # === EMOTIONAL REGULATION ===
        ("I calm myself down", "feeling overwhelmed by fear", "EMOTIONAL_MASTERY",
         "Calming down = emotional regulation"),
        
        ("I take deep breaths", "panic rising", "EMOTIONAL_MASTERY",
         "Deep breaths = self-soothing"),
        
        # === MAGICAL/SUPERNATURAL ===
        ("I use my powers to fly", "needing to escape danger", "MYTHICAL_MASTERY",
         "Using powers = supernatural mastery"),
        
        ("An angel protects me", "being threatened", "MYTHICAL_MASTERY",
         "Divine protection = supernatural"),
        
        # === NARRATIVE/AFFECT (no action) ===
        ("I see a dark forest", "entering the dream", "ZDPCS_NARRATIVE_SETTING",
         "Describing scene = narrative"),
        
        ("I feel terrified", "facing the monster", "ZDPCS_AFFECT_EXPRESSION",
         "Expressing fear = affect expression"),
        
        # === CRITICAL: NEGATION HANDLING ===
        ("I decide not to run", "being chased", "BEHAVIORAL_MASTERY",
         "Choosing NOT to flee = assertive choice"),
        
        ("I refuse to hide", "threat approaching", "BEHAVIORAL_MASTERY",
         "Refusing to hide = confronting"),
        
        ("I won't freeze this time", "facing my fear", "BEHAVIORAL_MASTERY",
         "Won't freeze = active response"),
        
        ("Instead of hiding, I stand firm", "monster appearing", "BEHAVIORAL_MASTERY",
         "Standing firm instead of hiding = adaptive"),
        
        # === AMBIGUOUS CASES (context changes meaning) ===
        ("I stay still", "wild animal nearby - playing dead", "ZDPCS_SAFETY_PRINCIPLE",
         "Staying still to avoid = avoidance"),
        
        ("I remain calm and still", "practicing mindfulness in the dream", "EMOTIONAL_MASTERY",
         "Calm stillness = emotional regulation"),
    ]
    
    print("\n" + "=" * 80)
    print("Test Results with Confidence Distribution")
    print("=" * 80)
    
    passed = 0
    type_match = 0
    failed = 0
    
    for action, context, expected, description in test_cases:
        # Get raw scores for all nodes
        premise = f"Context: {context} | Action: {action}"
        node_ids = list(classifier.node_hypotheses.keys())
        pairs = [(premise, classifier.node_hypotheses[node]) for node in node_ids]
        
        # Get raw scores
        scores = classifier.model.predict(pairs, convert_to_numpy=True)
        
        # Handle output shape
        if len(scores.shape) == 1:
            entailment_scores = scores
        else:
            entailment_scores = scores[:, classifier.entailment_idx]
        
        # Convert to percentages using softmax
        probabilities = softmax(entailment_scores) * 100
        
        # Get results
        best_idx = int(np.argmax(entailment_scores))
        result = node_ids[best_idx]
        best_prob = probabilities[best_idx]
        
        # Get expected info
        expected_type = classifier.get_node_info(expected).get("type")
        actual_type = classifier.get_node_info(result).get("type")
        
        # Determine status
        if result == expected:
            status = "✅"
            passed += 1
        elif actual_type == expected_type:
            status = "⚠️"
            type_match += 1
        else:
            status = "❌"
            failed += 1
        
        # Type emoji
        type_emoji = {"adaptive": "✅", "maladaptive": "⚠️", "neutral": "🟡"}.get(actual_type, "❓")
        
        print(f"\n{status} {description}")
        print(f"   Action: \"{action}\"")
        print(f"   Context: \"{context}\"")
        print(f"   Result: {type_emoji} {result} ({best_prob:.1f}%)")
        
        if result != expected:
            expected_idx = node_ids.index(expected)
            expected_prob = probabilities[expected_idx]
            print(f"   Expected: {expected} ({expected_prob:.1f}%)")
        
        # Show top 3 confidence distribution
        sorted_indices = np.argsort(probabilities)[::-1]
        print(f"   Confidence Distribution (top 5):")
        for i, idx in enumerate(sorted_indices[:5]):
            node = node_ids[idx]
            prob = probabilities[idx]
            bar_len = int(prob / 5)  # Scale for display
            bar = "█" * bar_len
            marker = " ← CHOSEN" if i == 0 else (" ← EXPECTED" if node == expected and result != expected else "")
            print(f"      {prob:5.1f}% {bar} {node}{marker}")
    
    # Summary
    total = len(test_cases)
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total tests: {total}")
    print(f"  ✅ Exact matches: {passed} ({passed/total*100:.1f}%)")
    print(f"  ⚠️  Type matches: {type_match} ({type_match/total*100:.1f}%)")
    print(f"  ❌ Misclassified: {failed} ({failed/total*100:.1f}%)")
    print(f"  Overall accuracy (exact + type): {(passed + type_match)/total*100:.1f}%")
    
    return failed == 0


async def main():
    """Run context-aware classification tests."""
    print("=" * 80)
    print("NLI-Based Clinical Classifier - Context-Aware Tests")
    print("=" * 80)
    
    try:
        success = await test_context_aware_classification()
        
        print("\n" + "=" * 80)
        if success:
            print("✅ All tests passed or matched expected type!")
        else:
            print("⚠️  Some classifications differ from expected.")
            print("   Review the confidence distributions above.")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
