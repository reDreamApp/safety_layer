#!/usr/bin/env python3
"""
Validation test set for NLI-Based Clinical Classifier

Fresh test cases NOT used during hypothesis optimization.
Tests generalization of the classifier to new phrasings and scenarios.
"""

import asyncio
import sys
import numpy as np
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())


def softmax(x):
    """Convert scores to probability distribution."""
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()


async def test_validation_set():
    """
    Validation test set with fresh examples not used during optimization.
    """
    print("\n" + "=" * 80)
    print("NLI Classifier VALIDATION Set (Fresh Examples)")
    print("=" * 80)
    
    from safety.classifier import ClinicalClassifier
    
    classifier = ClinicalClassifier()
    
    print(f"\nModel: {classifier.model_name}")
    print("Testing generalization to unseen phrasings...")
    
    # VALIDATION TEST CASES - different phrasings than training set
    # Format: (action, context, expected_node, description)
    test_cases = [
        # === BEHAVIORAL MASTERY - new phrasings ===
        ("I attack the creature", "monster blocking my path", "BEHAVIORAL_MASTERY",
         "Attacking creature = fighting"),
        
        ("I kick the door down", "trying to escape a locked room", "BEHAVIORAL_MASTERY",
         "Kicking door = physical action"),
        
        ("I grab it by the throat", "being cornered by attacker", "BEHAVIORAL_MASTERY",
         "Grabbing throat = confrontation"),
        
        ("I tackle the intruder", "someone breaking into my house", "BEHAVIORAL_MASTERY",
         "Tackling = physical resistance"),
        
        ("I swing my fist at it", "face to face with enemy", "BEHAVIORAL_MASTERY",
         "Swinging fist = fighting"),
        
        # === SOCIAL MASTERY - new phrasings ===
        ("I scream for someone to help me", "being dragged away", "SOCIAL_MASTERY",
         "Screaming for help = seeking assistance"),
        
        ("My mother appears and hugs me", "feeling alone and scared", "SOCIAL_MASTERY",
         "Mother appearing = receiving support"),
        
        ("I reach out to my brother", "facing danger together", "SOCIAL_MASTERY",
         "Reaching to brother = social connection"),
        
        ("A stranger comes to my rescue", "about to be attacked", "SOCIAL_MASTERY",
         "Stranger rescuing = receiving help"),
        
        # === ENVIRONMENTAL MASTERY - new phrasings ===
        ("I grab a knife from the kitchen", "intruder in my home", "ENVIRONMENTAL_MASTERY",
         "Grabbing knife = finding tool"),
        
        ("The walls suddenly become transparent", "trapped in darkness", "ENVIRONMENTAL_MASTERY",
         "Walls changing = environment transforms"),
        
        ("I notice an unlocked window", "looking for escape", "ENVIRONMENTAL_MASTERY",
         "Noticing window = discovering resource"),
        
        ("A ladder appears on the wall", "trying to climb out", "ENVIRONMENTAL_MASTERY",
         "Ladder appearing = environment provides"),
        
        # === EMOTIONAL MASTERY - new phrasings ===
        ("I steady my breathing", "heart racing with fear", "EMOTIONAL_MASTERY",
         "Steadying breath = emotional regulation"),
        
        ("I tell myself it's just a dream", "feeling panicked", "EMOTIONAL_MASTERY",
         "Self-talk = managing emotions"),
        
        ("I accept what's happening", "chaos around me", "EMOTIONAL_MASTERY",
         "Accepting = emotional regulation"),
        
        ("I focus on staying grounded", "world spinning", "EMOTIONAL_MASTERY",
         "Staying grounded = presence"),
        
        # === MYTHICAL MASTERY - new phrasings ===
        ("I shoot lightning from my hands", "surrounded by enemies", "MYTHICAL_MASTERY",
         "Lightning powers = supernatural"),
        
        ("I transform into a giant", "facing small attackers", "MYTHICAL_MASTERY",
         "Transforming = supernatural ability"),
        
        ("A ghost of my grandmother protects me", "in danger", "MYTHICAL_MASTERY",
         "Ghost protecting = supernatural help"),
        
        ("I teleport to safety", "about to be caught", "MYTHICAL_MASTERY",
         "Teleporting = supernatural"),
        
        # === ZDPCS_SAFETY_PRINCIPLE - new phrasings ===
        ("I duck behind the couch", "shooter in the room", "ZDPCS_SAFETY_PRINCIPLE",
         "Ducking behind = hiding"),
        
        ("I pretend to be dead", "predator sniffing around", "ZDPCS_SAFETY_PRINCIPLE",
         "Playing dead = avoidance"),
        
        ("I just stand there paralyzed", "danger approaching", "ZDPCS_SAFETY_PRINCIPLE",
         "Standing paralyzed = freezing"),
        
        ("I curl up in a ball", "being attacked", "ZDPCS_SAFETY_PRINCIPLE",
         "Curling up = passive avoidance"),
        
        ("I close my eyes and wait", "monster nearby", "ZDPCS_SAFETY_PRINCIPLE",
         "Closing eyes = avoidance"),
        
        # === ZDPCS_INTERRUPT - new phrasings ===
        ("I pinch myself to wake up", "nightmare getting worse", "ZDPCS_INTERRUPT",
         "Pinching to wake = ending dream"),
        
        ("I tell myself to open my eyes", "wanting to escape dream", "ZDPCS_INTERRUPT",
         "Opening eyes = waking up"),
        
        ("Everything goes black and I'm awake", "being chased", "ZDPCS_INTERRUPT",
         "Going black = dream ending"),
        
        ("I snap out of the dream", "about to die", "ZDPCS_INTERRUPT",
         "Snapping out = interrupting"),
        
        # === ZDPCS_REGRESSIVE_AGGRESSION - new phrasings ===
        ("I massacre them all", "enemies everywhere", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Massacring = extreme violence"),
        
        ("I rip them apart with my bare hands", "surrounded by attackers", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Ripping apart = brutal violence"),
        
        ("I burn the whole place down", "trapped in building", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Burning down = destruction"),
        
        ("I slaughter everyone I see", "people chasing me", "ZDPCS_REGRESSIVE_AGGRESSION",
         "Slaughtering = mass violence"),
        
        # === ZDPCS_NARRATIVE_SETTING - new phrasings ===
        ("The hallway stretches endlessly", "exploring the building", "ZDPCS_NARRATIVE_SETTING",
         "Hallway stretching = scene description"),
        
        ("There are shadows moving on the walls", "in a dark room", "ZDPCS_NARRATIVE_SETTING",
         "Shadows moving = observing"),
        
        ("I notice blood on the floor", "entering a room", "ZDPCS_NARRATIVE_SETTING",
         "Noticing blood = observing"),
        
        ("The sky turns red", "looking up", "ZDPCS_NARRATIVE_SETTING",
         "Sky changing = scene description"),
        
        # === ZDPCS_AFFECT_EXPRESSION - new phrasings ===
        ("I'm absolutely petrified", "facing the monster", "ZDPCS_AFFECT_EXPRESSION",
         "Petrified = expressing fear"),
        
        ("My heart is pounding out of my chest", "in danger", "ZDPCS_AFFECT_EXPRESSION",
         "Heart pounding = expressing fear"),
        
        ("I feel a deep sense of dread", "something approaching", "ZDPCS_AFFECT_EXPRESSION",
         "Feeling dread = emotion expression"),
        
        ("Panic overwhelms me", "being chased", "ZDPCS_AFFECT_EXPRESSION",
         "Panic overwhelming = expressing emotion"),
    ]
    
    print("\n" + "=" * 80)
    print("Validation Results")
    print("=" * 80)
    
    passed = 0
    type_match = 0
    failed = 0
    
    results_by_category = {}
    
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
        
        # Track by category
        if expected not in results_by_category:
            results_by_category[expected] = {"pass": 0, "type": 0, "fail": 0}
        
        # Determine status
        if result == expected:
            status = "✅"
            passed += 1
            results_by_category[expected]["pass"] += 1
        elif actual_type == expected_type:
            status = "⚠️"
            type_match += 1
            results_by_category[expected]["type"] += 1
        else:
            status = "❌"
            failed += 1
            results_by_category[expected]["fail"] += 1
        
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
        print(f"   Top 3: ", end="")
        top3 = [(node_ids[idx], probabilities[idx]) for idx in sorted_indices[:3]]
        print(", ".join([f"{n} ({p:.1f}%)" for n, p in top3]))
    
    # Summary by category
    print("\n" + "=" * 80)
    print("Results by Category")
    print("=" * 80)
    
    for cat, counts in sorted(results_by_category.items()):
        total = counts["pass"] + counts["type"] + counts["fail"]
        accuracy = (counts["pass"] + counts["type"]) / total * 100
        print(f"  {cat}: {counts['pass']}✅ {counts['type']}⚠️ {counts['fail']}❌ ({accuracy:.0f}%)")
    
    # Overall summary
    total = len(test_cases)
    print("\n" + "=" * 80)
    print("Overall Summary")
    print("=" * 80)
    print(f"Total validation tests: {total}")
    print(f"  ✅ Exact matches: {passed} ({passed/total*100:.1f}%)")
    print(f"  ⚠️  Type matches: {type_match} ({type_match/total*100:.1f}%)")
    print(f"  ❌ Misclassified: {failed} ({failed/total*100:.1f}%)")
    print(f"  Overall accuracy (exact + type): {(passed + type_match)/total*100:.1f}%")
    
    return failed <= total * 0.3  # Pass if less than 30% misclassified


async def main():
    """Run validation tests."""
    print("=" * 80)
    print("NLI Classifier Validation Set")
    print("(Testing generalization to unseen examples)")
    print("=" * 80)
    
    try:
        success = await test_validation_set()
        
        print("\n" + "=" * 80)
        if success:
            print("✅ Validation passed! Model generalizes well to new examples.")
        else:
            print("⚠️  Validation shows some generalization issues.")
            print("   Consider if hypotheses are too specific to training examples.")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
