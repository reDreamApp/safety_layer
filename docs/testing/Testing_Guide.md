# SafetyCritic Testing Guide

This document explains how to test the SafetyCritic "Clinical Reasoning Engine" that evaluates user dream rewriting attempts for therapeutic safety.

## Overview

The testing script (`test_critic_interactive.py`) supports multiple modes:

| Mode | Command | Use Case |
|------|---------|----------|
| **Scenario** | `--scenario FILE` | Run test suite against a specific nightmare |
| **Interactive** | `--context FILE` | Load nightmare, test manually |
| **Live** | `--live` | Chat through actual IRT flow |
| **Batch** | `--batch FILE` | Legacy testing without nightmare context |

## Recommended Testing Flow

### 1. Scenario Testing (Best for Systematic Testing)

Run a test suite where multiple rewriting attempts are evaluated against the same nightmare:

```bash
python test_critic_interactive.py --scenario scenarios/chase_scenario_tests.json
```

**Output includes:**
- The nightmare displayed prominently
- Each test input and its segmentation
- Classification of each segment
- Safety verdict (SAFE/UNSAFE with severity)
- Pass/fail against expected result
- Summary statistics

**Add `-v` for verbose output (shows constraint messages):**
```bash
python test_critic_interactive.py --scenario scenarios/chase_scenario_tests.json -v
```

### 2. Interactive Testing (Best for Exploration)

Load a nightmare context and manually type rewriting attempts:

```bash
python test_critic_interactive.py --context scenarios/chase_nightmare.json
```

**Commands in interactive mode:**
- Type any text to test it through the critic
- `examples` - Show example test cases
- `graph` - Show knowledge graph summary
- `context` - Re-display the nightmare
- `q` - Quit

### 3. Live Mode (Best for End-to-End Testing)

Chat through the actual IRT chatbot to reach rewriting stage naturally:

```bash
python test_critic_interactive.py --live
```

**Flow:**
1. Describe your nightmare to the therapist (RECORDING stage)
2. Agree to move to rewriting (REWRITING stage)
3. Critic testing mode activates automatically
4. Your rewriting attempts are analyzed

**Commands:**
- `history` - Show full conversation
- `skip` - Jump to rewriting with example nightmare
- `q` - Quit

## File Formats

### Scenario Test File (Recommended)

```json
{
  "name": "Chase Nightmare Test Suite",
  "nightmare": "I'm running through a dark forest. Something is chasing me...",
  "notes": "Testing avoidance vs. engagement responses",
  "test_cases": [
    {
      "description": "Adaptive - turn and fight",
      "input": "I turn around and face whatever is chasing me",
      "expected_safe": true
    },
    {
      "description": "Maladaptive - hide",
      "input": "I hide behind a tree",
      "expected_safe": false
    }
  ]
}
```

### Context File (For Interactive Testing)

```json
{
  "nightmare_summary": "I'm running through a dark forest...",
  "stage": "rewriting",
  "notes": "Optional testing notes"
}
```

### Legacy Batch File

```json
[
  {
    "description": "Test case name",
    "input": "The text to test",
    "expected_safe": true
  }
]
```

## Understanding the Output

### Segmentation

The critic first segments the input into parts:

```
Segments:
  [ACTION] "I turn around" → BEHAVIORAL MASTERY
  [FEELING] "I felt scared" → AFFECT EXPRESSION
  [META] "This is stupid" → (filtered out)
```

**Segment Types:**
- **ACTION** - User describes doing something in the dream
- **THOUGHT** - User describes a decision or realization
- **FEELING** - User expresses an emotion
- **META** - Conversational/resistance content (filtered out)

### Classification

Each non-META segment is mapped to a graph node:

```
Classification:
  • "I turn around"
    → BEHAVIORAL_MASTERY (adaptive)
  • "I felt scared"  
    → AFFECT_EXPRESSION (neutral)
```

**Node Types:**
- **adaptive** (green) - Healthy coping responses
- **maladaptive** (red) - Responses that need redirection
- **neutral** (yellow) - Context without action

### Triage (For Unsafe Inputs)

When multiple maladaptive patterns are detected, the critic selects the most critical:

```
Triage Decision:
  Primary risk: VIOLENT_REVENGE
  Severity: CRITICAL
```

**Severity Levels:**
1. **CRITICAL** - Violence (`VIOLENT_REVENGE`)
2. **HIGH** - Escape/Wake up (`INTERRUPTION`)
3. **MODERATE** - Avoidance (`AVOIDANCE`)

### Verdict

```
✅ SAFE → BEHAVIORAL_MASTERY
```
or
```
⚠️  UNSAFE (CRITICAL) → VIOLENT_REVENGE
```

## Knowledge Graph Nodes

### Maladaptive (Risks)
| Node | Category | Severity | Examples |
|------|----------|----------|----------|
| `AVOIDANCE` | Avoidance | MODERATE | Hiding, freezing, doing nothing |
| `INTERRUPTION` | Escape | HIGH | Waking up, ending the dream |
| `VIOLENT_REVENGE` | Violence | CRITICAL | Killing everyone, destroying everything |

### Adaptive (Goals)
| Node | Category | Examples |
|------|----------|----------|
| `BEHAVIORAL_MASTERY` | Action | Fighting back, confronting, running purposefully |
| `SOCIAL_MASTERY` | Help | Calling for help, allies appearing |
| `ENVIRONMENTAL_MASTERY` | Tools | Finding weapons, environment changing |
| `EMOTIONAL_MASTERY` | Self-regulation | Calming down, staying present |
| `MYTHICAL_MASTERY` | Supernatural | Magic powers, divine intervention |

### Neutral (Context)
| Node | Category | Examples |
|------|----------|----------|
| `NARRATIVE_SETTING` | Scene | "There was a dark forest" |
| `AFFECT_EXPRESSION` | Feeling | "I felt scared" |

## Creating Test Scenarios

### Best Practices

1. **One nightmare, many tests** - Test various responses against the same nightmare
2. **Cover all node types** - Include adaptive, maladaptive, neutral, and mixed inputs
3. **Test edge cases**:
   - Negation: "I decided NOT to run"
   - Mixed: "I hate this, but I fight back"
   - Multi-part: "I felt scared. Then I called for help."
4. **Include META resistance** - "This is stupid", "I don't want to do this"

### Example Test Categories

```json
{
  "test_cases": [
    // Adaptive responses
    {"description": "Fight back", "input": "I punch the monster", "expected_safe": true},
    {"description": "Call for help", "input": "I shout for someone to help", "expected_safe": true},
    
    // Maladaptive responses  
    {"description": "Wake up", "input": "I force myself awake", "expected_safe": false},
    {"description": "Hide", "input": "I hide and hope it goes away", "expected_safe": false},
    {"description": "Extreme violence", "input": "I kill everyone", "expected_safe": false},
    
    // Neutral (should pass)
    {"description": "Feeling only", "input": "I felt terrified", "expected_safe": true},
    {"description": "Scene description", "input": "The room was dark", "expected_safe": true},
    
    // Mixed inputs
    {"description": "META + action", "input": "This is dumb but I fight back", "expected_safe": true},
    {"description": "Feeling + violence", "input": "I was angry so I killed them", "expected_safe": false},
    
    // Negation handling
    {"description": "Decided not to run", "input": "I decided not to run away", "expected_safe": true}
  ]
}
```

## Troubleshooting

### Common Issues

**"Critic not initialized"**
- Check that your `.env` file has `GROQ_API_KEY` set
- Verify network connectivity

**Unexpected classifications**
- The LLM classifier may interpret ambiguous inputs differently
- Check the segmentation output to see how the input was parsed
- Try rephrasing the input to be more explicit

**Pass rate below expectations**
- Review failed cases to understand mismatches
- Some edge cases may need prompt engineering adjustments
- META content should always pass (filtered out)

## File Locations

```
code/
├── test_critic_interactive.py    # Main test script
├── scenarios/
│   ├── chase_nightmare.json      # Context file
│   ├── chase_scenario_tests.json # Scenario test suite
│   ├── confrontation_nightmare.json
│   └── batch_tests.json          # Legacy batch tests
└── Documents/
    └── Testing_Guide.md          # This file
```
