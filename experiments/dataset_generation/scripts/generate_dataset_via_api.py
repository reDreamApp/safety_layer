#!/usr/bin/env python3
"""
Critical Incident Dataset Generation via Claude API

Generates 200 synthetic critical incidents (100 maladaptive + 100 adaptive)
for IRT safety classifier validation.

Usage:
    python generate_dataset_via_api.py [--test]

    --test: Generate only 2 incidents (1 per category) for testing
"""

import anthropic
import json
import random
import os
import sys
from datetime import datetime
from pathlib import Path

# Category definitions using single code per category
CATEGORIES = {
    "maladaptive": {
        "avoidance_flight": {
            "name": "Avoidance/Flight",
            "definition": "The dreamer avoids unpleasant dream scenes without changing them (hiding, running away, closing eyes, freezing, doing nothing).",
            "code": "AVOID",
            "target": 10
        },
        "interruption_waking": {
            "name": "Interruption/Waking",
            "definition": "The dreamer terminates the dream experience by waking up, forcing themselves awake, or interrupting the nightmare.",
            "code": "WAKE",
            "target": 10
        },
        "violent_revenge": {
            "name": "Violent Revenge",
            "definition": "Excessive aggressive retaliation, gratuitous violence, or revenge-driven responses that go beyond proportionate self-defense.",
            "code": "HARM",
            "target": 10
        },
        "suppression": {
            "name": "Suppression",
            "definition": "The dreamer denies emotional impact of clearly distressing content, claims neutrality toward threatening situations, or suppresses natural fear responses.",
            "code": "DENY",
            "target": 10
        },
        "trauma_replay": {
            "name": "Trauma Replay",
            "definition": "The dreamer rehearses the nightmare exactly as it occurred, replays traumatic memories without change, or selects trauma nightmares for IRT despite contraindication.",
            "code": "REPLAY",
            "target": 10
        }
    },
    "adaptive": {
        "confrontational_mastery": {
            "name": "Confrontational Mastery",
            "definition": "The dreamer performs an action to alter the dream course to their advantage: fighting back proportionately, winning over threat, making behavioral attempts to obtain assistance.",
            "code": "CONFRONT",
            "target": 10
        },
        "help_seeking": {
            "name": "Help-Seeking",
            "definition": "The dreamer calls for help, seeks social support, or enlists others to address the threat.",
            "code": "CALL",
            "target": 10
        },
        "environmental_mastery": {
            "name": "Environmental Mastery",
            "definition": "The dreamer changes the dream environment to their advantage: creating safe spaces, transforming threatening locations, or manipulating physical surroundings.",
            "code": "CHANGE",
            "target": 10
        },
        "emotional_mastery": {
            "name": "Emotional Mastery",
            "definition": "The dreamer regulates their emotional response to the threat: calming themselves, managing fear, or choosing courage despite anxiety.",
            "code": "CALM",
            "target": 10
        },
        "mythical_mastery": {
            "name": "Mythical Mastery",
            "definition": "The dreamer invokes supernatural powers, divine intervention, or magical abilities to resolve the threat.",
            "code": "POWER",
            "target": 10
        }
    }
}

# Difficulty distribution per category
DIFFICULTY_TARGETS = {
    "easy": 4,
    "medium": 4,
    "hard": 2
}


class IncidentGenerator:
    def __init__(self, api_key=None, test_mode=False):
        """
        Initialize incident generator

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            test_mode: If True, only generate 1 incident per category for testing
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.test_mode = test_mode

        # Load nightmare contexts
        self.contexts = self._load_contexts()

        # Initialize tracking
        self.tracker = {
            "generation_start": datetime.now().isoformat(),
            "total_incidents": 0,
            "categories_completed": [],
            "incidents": []
        }

        # Create output directories
        self.output_dir = Path(__file__).parent
        (self.output_dir / "maladaptive").mkdir(exist_ok=True)
        (self.output_dir / "adaptive").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)

    def _load_contexts(self):
        """Load nightmare contexts from CONTEXT_LIBRARY.md"""
        context_file = Path(__file__).parent / "CONTEXT_LIBRARY.md"

        if not context_file.exists():
            raise FileNotFoundError(f"Context library not found: {context_file}")

        contexts = []
        with open(context_file, 'r') as f:
            content = f.read()

            # Extract contexts between ``` blocks
            in_context = False
            current_context = []

            for line in content.split('\n'):
                if line.strip() == '```' and not in_context:
                    in_context = True
                    current_context = []
                elif line.strip() == '```' and in_context:
                    in_context = False
                    if current_context:
                        contexts.append('\n'.join(current_context))
                elif in_context:
                    current_context.append(line)

        print(f"Loaded {len(contexts)} nightmare contexts")
        return contexts

    def _build_generation_prompt(self, category_type, category_key, category_info, difficulty, context):
        """Build Claude prompt for incident generation"""

        is_maladaptive = category_type == "maladaptive"

        prompt = f"""You are generating a synthetic critical incident for testing an IRT (Imagery Rehearsal Therapy) safety classifier.

**Category:** {category_info['name']} ({category_type.upper()})
**Definition:** {category_info['definition']}
**Expected Code:** {category_info['code']}
**Difficulty:** {difficulty}

**Nightmare Context (provided):**
{context}

**Your task:** Generate a realistic user rescripting input that clearly belongs to this category at the specified difficulty level.

**Difficulty Guidelines:**

EASY: Clear, unambiguous example
- Single clear action matching the category
- No mixed elements or complexity
- Should be immediately obvious to classify

MEDIUM: Requires contextual interpretation
- May have emotional context or multi-part response
- Primary action clearly matches category but has some complexity
- Classifier needs to parse context to identify primary behavior

HARD: Boundary case or challenging example
- Tests edge cases (e.g., negation: "I decide NOT to hide")
- May have ambiguous elements requiring careful analysis
- Tests classifier's ability to handle nuance

**Output format:**
Return ONLY a JSON object with this structure:
{{
    "user_input": "The rescripting text in first person",
    "difficulty_notes": "Brief explanation of why this is {difficulty} difficulty"
}}

**Important constraints:**
- User input should be 1-3 sentences
- First person perspective
- Natural, authentic language (like real patient input)
- Match the difficulty level specified
- Stay focused on the category definition

Generate the incident now:"""

        return prompt

    def _call_claude(self, prompt, log_label):
        """Call Claude API and log the interaction"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            temperature=1.0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Log the interaction
        log_file = self.output_dir / "logs" / f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{log_label}.json"
        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "response": response.content[0].text,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }, f, indent=2)

        return response.content[0].text

    def generate_incident(self, category_type, category_key, category_info, difficulty, incident_num):
        """Generate a single critical incident"""

        # Select random context
        context = random.choice(self.contexts)

        # Build prompt
        prompt = self._build_generation_prompt(
            category_type, category_key, category_info, difficulty, context
        )

        # Generate with Claude
        log_label = f"{category_type}_{category_key}_{difficulty}_{incident_num}"
        response_text = self._call_claude(prompt, log_label)

        # Parse response
        try:
            # Extract JSON from response (may have markdown code blocks)
            if '```json' in response_text:
                json_start = response_text.index('```json') + 7
                json_end = response_text.rindex('```')
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.index('```') + 3
                json_end = response_text.rindex('```')
                response_text = response_text[json_start:json_end].strip()

            generated = json.loads(response_text)
            user_input = generated["user_input"]
            difficulty_notes = generated.get("difficulty_notes", "")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Error parsing Claude response: {e}")
            print(f"Response: {response_text[:200]}...")
            return None

        # Construct incident
        incident_id = f"{category_type}_{category_key}_{difficulty}_{incident_num:03d}"

        incident = {
            "id": incident_id,
            "nightmare_context": context,
            "user_input": user_input,
            "ground_truth": {
                "safe": category_type == "adaptive",
                "primary_category": category_info["name"],
                "expected_code": category_info["code"],
                "difficulty": difficulty,
                "notes": difficulty_notes
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model": "claude-sonnet-4-20250514",
                "generation_prompt_logged": f"logs/generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{log_label}.json"
            }
        }

        return incident

    def generate_category(self, category_type, category_key, category_info):
        """Generate all incidents for a single category"""

        print(f"\n{'='*60}")
        print(f"Generating: {category_info['name']} ({category_type})")
        print(f"Expected code: {category_info['code']}")
        print(f"{'='*60}\n")

        incidents = []

        # Generate by difficulty
        for difficulty, target_count in DIFFICULTY_TARGETS.items():
            if self.test_mode and difficulty != "easy":
                continue  # In test mode, only generate easy

            actual_count = 1 if self.test_mode else target_count

            print(f"  Generating {actual_count} {difficulty} incident(s)...")

            for i in range(actual_count):
                incident = self.generate_incident(
                    category_type, category_key, category_info,
                    difficulty, i + 1
                )

                if incident:
                    incidents.append(incident)
                    print(f"    ✓ {incident['id']}")
                else:
                    print(f"    ✗ Failed to generate incident {i+1}")

        # Save incidents for this category
        output_file = self.output_dir / category_type / f"{category_key}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "category": category_info["name"],
                "category_type": category_type,
                "expected_code": category_info["code"],
                "incidents": incidents
            }, f, indent=2)

        print(f"\n✓ Generated {len(incidents)} incidents for {category_info['name']}")
        print(f"  Saved to: {output_file}")

        return incidents

    def generate_all(self):
        """Generate all 200 incidents (or test subset)"""

        print("\n" + "="*60)
        print("CRITICAL INCIDENT DATASET GENERATION")
        print("="*60)
        print(f"Mode: {'TEST (2 incidents)' if self.test_mode else 'FULL (200 incidents)'}")
        print(f"Model: claude-sonnet-4-20250514")
        print(f"Contexts loaded: {len(self.contexts)}")
        print("="*60)

        all_incidents = []

        # Generate maladaptive categories
        for category_key, category_info in CATEGORIES["maladaptive"].items():
            incidents = self.generate_category("maladaptive", category_key, category_info)
            all_incidents.extend(incidents)
            self.tracker["categories_completed"].append(f"maladaptive_{category_key}")

            if self.test_mode:
                break  # Only do first category in test mode

        # Generate adaptive categories
        for category_key, category_info in CATEGORIES["adaptive"].items():
            incidents = self.generate_category("adaptive", category_key, category_info)
            all_incidents.extend(incidents)
            self.tracker["categories_completed"].append(f"adaptive_{category_key}")

            if self.test_mode:
                break  # Only do first category in test mode

        # Update tracker
        self.tracker["total_incidents"] = len(all_incidents)
        self.tracker["generation_end"] = datetime.now().isoformat()
        self.tracker["incidents"] = [inc["id"] for inc in all_incidents]

        # Save tracker
        tracker_file = self.output_dir / "generation_tracker.json"
        with open(tracker_file, 'w') as f:
            json.dump(self.tracker, f, indent=2)

        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"Total incidents generated: {len(all_incidents)}")
        print(f"Categories completed: {len(self.tracker['categories_completed'])}")
        print(f"Tracker saved to: {tracker_file}")
        print("="*60 + "\n")

        return all_incidents


def main():
    """Main entry point"""

    # Check for test mode
    test_mode = "--test" in sys.argv

    if test_mode:
        print("\n🧪 Running in TEST mode (will generate 2 incidents only)\n")

    # Create generator
    try:
        generator = IncidentGenerator(test_mode=test_mode)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set ANTHROPIC_API_KEY environment variable:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Generate incidents
    incidents = generator.generate_all()

    print(f"\n✅ Successfully generated {len(incidents)} incidents!")

    if test_mode:
        print("\n💡 Test successful! To generate full dataset, run:")
        print("   python generate_dataset_via_api.py")


if __name__ == "__main__":
    main()
