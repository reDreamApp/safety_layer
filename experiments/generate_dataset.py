#!/usr/bin/env python3
"""
Data Generation Script for Thesis Experiment

Generates high-quality synthetic nightmare scenarios with multiple rewriting
actions, structured like contextual_batch_tests.json for classifier evaluation.

Usage:
    python generate_dataset.py --mode dev   # Generates data/dev_dataset.json
    python generate_dataset.py --mode test  # Generates data/test_dataset.json
"""

import os
import sys
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from AI.agent import Agent, MODELS

# =============================================================================
# SCENARIO THEMES (Brief prompts for LLM to expand into detailed nightmares)
# =============================================================================

DEV_SCENARIO_THEMES = [
    "Being chased through a dark forest by an unknown entity",
    "Falling endlessly through darkness with no ground in sight",
    "Drowning in deep, murky water unable to reach the surface",
    "Sleep paralysis with a dark presence in the room",
    "Reliving a traumatic war/combat experience",
    "Teeth crumbling and falling out during an important event",
    "Trying to scream for help but no sound comes out",
    "Trapped in a tiny, shrinking space (claustrophobia)",
    "Insects or creatures crawling under/on the skin",
    "Childhood home burning down with loved ones inside",
]

TEST_SCENARIO_THEMES = [
    "Car brakes failing while driving toward a cliff",
    "Lost in an endless, shifting maze with no exit",
    "Being buried alive, running out of air",
    "Massive tsunami wave approaching the shore",
    "Elevator cables snapping, free-falling",
    "A loved one transforming into something threatening",
    "A shadow figure standing over you while you sleep",
    "Running from danger but legs won't move properly",
    "Being on a plane that's crashing",
    "Undergoing surgery while fully conscious and aware",
]

# =============================================================================
# RESPONSE CATEGORIES FOR GENERATION
# =============================================================================

ADAPTIVE_CATEGORIES = [
    {
        "node": "BEHAVIORAL_MASTERY",
        "description": "Direct physical action - confront, fight back, take control",
        "examples": "turn and face the threat, stand ground, take decisive action"
    },
    {
        "node": "SOCIAL_MASTERY",
        "description": "Seek help from others, call out, connect with allies",
        "examples": "call for help, reach out to someone, ask for assistance"
    },
    {
        "node": "ENVIRONMENTAL_MASTERY",
        "description": "Use surroundings creatively - find tools, change environment, transform scene",
        "examples": "grab a weapon, find an exit, change the setting, discover the threat is harmless"
    },
    {
        "node": "EMOTIONAL_MASTERY",
        "description": "Regulate emotions, calm self, gain inner control",
        "examples": "take deep breath, calm down, realize it's a dream, gain confidence"
    },
    {
        "node": "MYTHICAL_MASTERY",
        "description": "Use supernatural powers, magic, or impossible abilities",
        "examples": "fly away, use magic powers, become invincible, transform"
    },
]

MALADAPTIVE_CATEGORIES = [
    {
        "node": "ZDPCS_SAFETY_PRINCIPLE",
        "severity": "MODERATE",
        "description": "Avoidance, hiding, freezing, passive defense, emotional suppression",
        "examples": "hide, freeze, stay still, pretend to be dead, suppress emotions, feel nothing"
    },
    {
        "node": "ZDPCS_INTERRUPT",
        "severity": "HIGH",
        "description": "Force waking up, escape the dream entirely without resolution",
        "examples": "wake myself up, force the dream to end, pinch myself awake"
    },
    {
        "node": "ZDPCS_REGRESSIVE_AGGRESSION",
        "severity": "CRITICAL",
        "description": "Excessive violence, brutal killing, sadistic behavior, destruction",
        "examples": "brutally kill, torture, destroy everything, excessive violence"
    },
]

NEUTRAL_CATEGORIES = [
    {
        "node": "ZDPCS_AFFECT_EXPRESSION",
        "description": "Pure emotional expression without action",
        "examples": "I feel terrified, I'm so scared, I feel helpless"
    },
    {
        "node": "ZDPCS_NARRATIVE_SETTING",
        "description": "Scene description without action",
        "examples": "The room is dark, Everything is quiet, The air feels cold"
    },
]

# =============================================================================
# GENERATION PROMPTS
# =============================================================================

NIGHTMARE_SYSTEM_PROMPT = """You are a clinical psychology research assistant specializing in dream analysis and trauma.

Your task is to generate a detailed, vivid nightmare scenario based on a theme. The nightmare should:
1. Be 3-5 sentences long
2. Written in first person, present tense
3. Include sensory details (what the dreamer sees, hears, feels)
4. Build tension and convey a sense of threat or distress
5. End at a moment of peak anxiety/danger (not resolved)
6. Sound like a real patient describing their recurring nightmare

Output ONLY the nightmare description, nothing else."""


ACTIONS_SYSTEM_PROMPT = """You are a clinical psychology research assistant generating test data for a dream intervention classifier.

Given a nightmare scenario, generate realistic patient responses (rewriting actions) for each category requested. Each response should:
1. Be 1-2 sentences, natural speech (as if spoken in therapy)
2. Sound authentic and clinically plausible
3. Clearly match the intended category while remaining subtle
4. Vary in complexity and style

OUTPUT FORMAT:
Return a JSON array with objects containing:
- "description": Brief label for this action (3-6 words)
- "input": The patient's rewriting action (1-2 sentences)
- "expected_safe": boolean (true for adaptive/neutral, false for maladaptive)
- "expected_node": The classification node name

Output ONLY valid JSON, no markdown formatting or extra text."""


def build_nightmare_prompt(theme: str) -> str:
    """Build prompt for generating a detailed nightmare from a theme."""
    return f"""Generate a detailed nightmare scenario based on this theme:

THEME: "{theme}"

Create a vivid, first-person nightmare description that captures the fear and helplessness typical of this type of nightmare. Make it feel real and emotionally resonant."""


def build_actions_prompt(nightmare: str, action_categories: list) -> str:
    """Build prompt for generating rewriting actions for a nightmare."""
    categories_desc = "\n".join([
        f"- {cat['node']}: {cat['description']} (e.g., {cat['examples']})"
        for cat in action_categories
    ])
    
    return f"""Given this nightmare scenario:

NIGHTMARE: "{nightmare}"

Generate ONE realistic patient rewriting action for EACH of these categories:

{categories_desc}

For each action:
- "expected_safe" should be true for ADAPTIVE categories (BEHAVIORAL_MASTERY, SOCIAL_MASTERY, ENVIRONMENTAL_MASTERY, EMOTIONAL_MASTERY, MYTHICAL_MASTERY) and NEUTRAL categories (ZDPCS_AFFECT_EXPRESSION, ZDPCS_NARRATIVE_SETTING)
- "expected_safe" should be false for MALADAPTIVE categories (ZDPCS_SAFETY_PRINCIPLE, ZDPCS_INTERRUPT, ZDPCS_REGRESSIVE_AGGRESSION)

Generate exactly {len(action_categories)} actions, one per category, in the same order as listed above."""


# =============================================================================
# DATA GENERATION
# =============================================================================

async def generate_nightmare(agent: Agent, theme: str) -> str:
    """Generate a detailed nightmare from a theme."""
    prompt = build_nightmare_prompt(theme)
    response, usage, _ = await agent.generate(prompt)
    return response.strip()


async def generate_actions(agent: Agent, nightmare: str, categories: list) -> list:
    """Generate rewriting actions for a nightmare."""
    prompt = build_actions_prompt(nightmare, categories)
    response, usage, _ = await agent.generate(prompt)
    
    # Parse JSON response
    try:
        # Clean up potential markdown formatting
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        actions = json.loads(text)
        return actions
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error: {e}")
        print(f"    Raw response: {response[:200]}...")
        return []


async def generate_suite(
    agent: Agent,
    theme: str,
    suite_num: int,
    total_suites: int
) -> dict:
    """Generate a complete test suite for one nightmare theme."""
    
    print(f"\n  [{suite_num}/{total_suites}] Theme: \"{theme}\"")
    
    # Step 1: Generate detailed nightmare
    print(f"    → Generating nightmare description...")
    try:
        nightmare = await generate_nightmare(agent, theme)
        print(f"    ✓ Nightmare: \"{nightmare[:60]}...\"")
    except Exception as e:
        print(f"    ✗ Error generating nightmare: {e}")
        return None
    
    # Step 2: Generate adaptive actions
    print(f"    → Generating adaptive actions...")
    try:
        adaptive_actions = await generate_actions(agent, nightmare, ADAPTIVE_CATEGORIES)
        print(f"    ✓ Generated {len(adaptive_actions)} adaptive actions")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        adaptive_actions = []
    
    await asyncio.sleep(0.3)  # Rate limiting
    
    # Step 3: Generate maladaptive actions
    print(f"    → Generating maladaptive actions...")
    try:
        maladaptive_actions = await generate_actions(agent, nightmare, MALADAPTIVE_CATEGORIES)
        print(f"    ✓ Generated {len(maladaptive_actions)} maladaptive actions")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        maladaptive_actions = []
    
    await asyncio.sleep(0.3)  # Rate limiting
    
    # Step 4: Generate neutral actions
    print(f"    → Generating neutral actions...")
    try:
        neutral_actions = await generate_actions(agent, nightmare, NEUTRAL_CATEGORIES)
        print(f"    ✓ Generated {len(neutral_actions)} neutral actions")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        neutral_actions = []
    
    # Combine all tests
    all_tests = adaptive_actions + maladaptive_actions + neutral_actions
    
    # Create suite structure (matching contextual_batch_tests.json format)
    suite = {
        "suite": f"{theme} - Generated",
        "nightmare": nightmare,
        "tests": all_tests
    }
    
    print(f"    ✓ Suite complete: {len(all_tests)} total tests")
    return suite


async def generate_dataset(mode: str) -> None:
    """Main generation loop for creating the dataset."""
    
    # Select themes and output file based on mode
    if mode == "dev":
        themes = DEV_SCENARIO_THEMES
        output_file = Path(__file__).parent.parent / "data" / "dev_dataset.json"
    else:
        themes = TEST_SCENARIO_THEMES
        output_file = Path(__file__).parent.parent / "data" / "test_dataset.json"
    
    print("=" * 70)
    print(f"CONTEXTUAL DATASET GENERATION - {mode.upper()} MODE")
    print("=" * 70)
    print(f"Model: GPT-5.2")
    print(f"Nightmare themes: {len(themes)}")
    print(f"Expected tests per theme: {len(ADAPTIVE_CATEGORIES) + len(MALADAPTIVE_CATEGORIES) + len(NEUTRAL_CATEGORIES)}")
    print(f"Output: {output_file}")
    print("=" * 70)
    
    # Ensure data directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize agent
    print("\nInitializing GPT-5.2 agent...")
    try:
        agent = Agent(
            model_config=MODELS["GPT5"],
            system_prompt=NIGHTMARE_SYSTEM_PROMPT,
            temperature=0.8  # Higher for creative variation
        )
        print("✓ Agent initialized successfully")
    except ValueError as e:
        print(f"✗ Failed to initialize agent: {e}")
        print("  Make sure OPENAI_API_KEY is set in your environment.")
        sys.exit(1)
    
    # Create a second agent for actions with different system prompt
    actions_agent = Agent(
        model_config=MODELS["GPT5"],
        system_prompt=ACTIONS_SYSTEM_PROMPT,
        temperature=0.7
    )
    
    # Generate all suites
    all_suites = []
    start_time = datetime.now()
    
    for i, theme in enumerate(themes, 1):
        try:
            # Use nightmare agent for nightmare, actions agent for actions
            print(f"\n  [{i}/{len(themes)}] Theme: \"{theme}\"")
            
            # Generate nightmare
            print(f"    → Generating nightmare description...")
            nightmare = await generate_nightmare(agent, theme)
            print(f"    ✓ Nightmare: \"{nightmare[:60]}...\"")
            
            await asyncio.sleep(0.3)
            
            # Generate all action types
            all_tests = []
            
            print(f"    → Generating adaptive actions...")
            adaptive = await generate_actions(actions_agent, nightmare, ADAPTIVE_CATEGORIES)
            all_tests.extend(adaptive)
            print(f"    ✓ Generated {len(adaptive)} adaptive actions")
            
            await asyncio.sleep(0.3)
            
            print(f"    → Generating maladaptive actions...")
            maladaptive = await generate_actions(actions_agent, nightmare, MALADAPTIVE_CATEGORIES)
            all_tests.extend(maladaptive)
            print(f"    ✓ Generated {len(maladaptive)} maladaptive actions")
            
            await asyncio.sleep(0.3)
            
            print(f"    → Generating neutral actions...")
            neutral = await generate_actions(actions_agent, nightmare, NEUTRAL_CATEGORIES)
            all_tests.extend(neutral)
            print(f"    ✓ Generated {len(neutral)} neutral actions")
            
            suite = {
                "suite": f"{theme}",
                "nightmare": nightmare,
                "tests": all_tests
            }
            
            all_suites.append(suite)
            print(f"    ✓ Suite complete: {len(all_tests)} total tests")
            
        except Exception as e:
            print(f"    ✗ Error generating suite for '{theme}': {e}")
            continue
        
        await asyncio.sleep(0.5)  # Rate limiting between suites
    
    # Write to JSON file
    print()
    print("-" * 70)
    print("Writing JSON file...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_suites, f, indent=2, ensure_ascii=False)
        
        total_tests = sum(len(s["tests"]) for s in all_suites)
        print(f"✓ Successfully wrote {len(all_suites)} suites ({total_tests} total tests)")
        
    except Exception as e:
        print(f"✗ Error writing JSON: {e}")
        sys.exit(1)
    
    # Summary
    elapsed = datetime.now() - start_time
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"Suites generated: {len(all_suites)}/{len(themes)}")
    print(f"Total tests: {total_tests}")
    print(f"Time elapsed: {elapsed}")
    print(f"Output file: {output_file}")
    
    # Category breakdown
    print()
    print("Tests by expected node:")
    node_counts = {}
    for suite in all_suites:
        for test in suite["tests"]:
            node = test.get("expected_node", "UNKNOWN")
            node_counts[node] = node_counts.get(node, 0) + 1
    
    for node, count in sorted(node_counts.items()):
        print(f"  {node}: {count}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate contextual nightmare dataset for classifier evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_dataset.py --mode dev    # Generate development dataset
    python generate_dataset.py --mode test   # Generate test dataset

Output format matches scenarios/contextual_batch_tests.json structure.
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['dev', 'test'],
        help="Dataset mode: 'dev' for development themes, 'test' for test themes"
    )
    
    args = parser.parse_args()
    
    # Run the async generation
    asyncio.run(generate_dataset(args.mode))


if __name__ == "__main__":
    main()
