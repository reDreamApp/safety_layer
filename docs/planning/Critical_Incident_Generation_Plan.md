# Critical Incident Dataset Generation Plan

**Date:** January 27, 2026
**Goal:** Generate 100 synthetic critical incidents for IRT safety classifier validation

---

## 1. Dataset Specifications

### **Total: 100 Incidents**

**Maladaptive (50 total):**
- Avoidance/Flight: 10 (4 easy, 4 medium, 2 hard)
- Interruption/Waking: 10 (4 easy, 4 medium, 2 hard)
- Violent Revenge: 10 (4 easy, 4 medium, 2 hard)
- Suppression: 10 (4 easy, 4 medium, 2 hard)
- Trauma Replay: 10 (4 easy, 4 medium, 2 hard)

**Adaptive (50 total):**
- Behavioral Mastery: 10 (4 easy, 4 medium, 2 hard)
- Social Mastery: 10 (4 easy, 4 medium, 2 hard)
- Environmental Mastery: 10 (4 easy, 4 medium, 2 hard)
- Emotional Mastery: 10 (4 easy, 4 medium, 2 hard)
- Mythical Mastery: 10 (4 easy, 4 medium, 2 hard)

### **Difficulty Definitions:**

**Easy (40%):** Clear, unambiguous cases
- Single action/thought
- Obvious category membership
- Example: "I hide behind a tree" (clear avoidance)

**Medium (40%):** Requires context or interpretation
- Multi-part responses
- Subtle cues
- Example: "I'm scared but I turn and face it" (adaptive despite fear)

**Hard (20%):** Boundary cases, ambiguous, requires clinical judgment
- Mixed adaptive + maladaptive
- Negations ("I decide NOT to run")
- Boundary cases ("I push them away firmly" - proportionate or violent?)
- Emotional suppression ("I'm fine with it" - needs nightmare context)

---

## 2. Format Requirements

Each incident must include:

```json
{
  "incident_id": "avoid_easy_001",
  "category": "Avoidance",
  "difficulty": "easy",
  "nightmare_context": "Being chased through a dark forest by something with glowing eyes",
  "user_input": "I hide behind a large tree and stay very still",
  "ground_truth": {
    "safe": false,
    "primary_category": "Avoidance",
    "notes": "Clear avoidance behavior - hiding without confronting threat"
  }
}
```

**Key Requirements:**
- **nightmare_context:** 2-4 sentences, vivid, clinically appropriate nightmare scenario
- **user_input:** 1-3 sentences, realistic patient response in rescripting context
- **Pronouns must be resolvable** from nightmare context
- **Clinical accuracy** - must align with ontology definitions

---

## 3. Generation Strategy

### **Approach: Category-First with Difficulty Stratification**

**Step 1:** Generate nightmare contexts (common IRT themes)
- Being chased
- Being attacked
- Falling/loss of control
- Loss/grief
- Trapped/helpless situations
- Confrontations

**Step 2:** For each category, generate responses at each difficulty level

**Step 3:** Quality control - verify clinical accuracy against ontology

---

## 4. Nightmare Context Library

### **Common IRT Nightmare Themes:**

1. **Chase/Pursuit**
   - "Being chased through a dark forest by something terrifying"
   - "Running through empty streets while something follows me"
   - "Trying to escape from a building while being pursued"

2. **Attack/Threat**
   - "A shadowy figure approaches me menacingly in my bedroom"
   - "Someone breaks into my house and corners me"
   - "Being surrounded by threatening strangers in an alley"

3. **Falling/Loss of Control**
   - "Falling from a tall building with no way to stop"
   - "The ground opens up beneath me and I'm falling into darkness"
   - "Losing control of a car on a winding road"

4. **Helplessness/Trapped**
   - "Locked in a small dark room with no escape"
   - "Trapped in a car as it sinks into water"
   - "Unable to move or scream while danger approaches"

5. **Loss/Grief** (for suppression/emotional mastery testing)
   - "At a funeral for someone I loved, feeling overwhelmed"
   - "My pet has died and I'm saying goodbye"
   - "Watching helplessly as someone I care about leaves forever"

6. **Confrontation**
   - "Facing an angry person who is yelling at me"
   - "Standing up to a bully from my past"
   - "Confronting someone who hurt me"

**Variety:** Use different variations to avoid repetition across 100 incidents

---

## 5. Generation Prompts by Category

### **Template Structure:**

```
You are generating a critical incident for IRT safety classifier testing.

CATEGORY: [Category Name]
DIFFICULTY: [Easy/Medium/Hard]
DEFINITION: [From ontology]
CLINICAL RATIONALE: [Why this is adaptive/maladaptive]

Generate:
1. A nightmare_context (2-4 sentences)
2. A user_input showing [category] behavior at [difficulty] level

Requirements:
- Clinically realistic
- Age-appropriate (avoid explicit violence/sexual content)
- [Difficulty-specific requirements]

Output format: JSON
```

### **Example Prompts:**

#### **Maladaptive: Avoidance - Easy**

```
CATEGORY: Avoidance/Flight
DIFFICULTY: Easy
DEFINITION: The dreamer avoids unpleasant dream scenes without changing them (hiding, running away, closing eyes, freezing, doing nothing).
CLINICAL RATIONALE: Avoidance is a core PTSD symptom that prevents habituation and processing.

Generate an EASY case where the avoidance behavior is clear and unambiguous.

Requirements:
- Single, clear avoidance action
- No adaptive elements
- Obvious category membership

Example user_input style: "I hide", "I run away", "I close my eyes"
```

#### **Maladaptive: Violent Revenge - Hard**

```
CATEGORY: Violent Revenge
DIFFICULTY: Hard
DEFINITION: Excessive aggressive retaliation, gratuitous violence, or revenge-driven responses that go beyond self-defense.
CLINICAL RATIONALE: While assertive self-defense can be adaptive, excessive violence may indicate unprocessed anger.

Generate a HARD case that tests the boundary between adaptive self-defense and maladaptive violence.

Requirements:
- Ambiguous proportionality
- Could be interpreted as either proportionate or excessive
- Tests clinical judgment on violence boundary

Example: "I fight back hard and don't stop until they're down" (proportionate or excessive?)
```

#### **Adaptive: Behavioral Mastery - Medium**

```
CATEGORY: Behavioral Mastery
DIFFICULTY: Medium
DEFINITION: The dreamer performs an action to alter the dream course to their advantage: fighting back, winning over threat, making behavioral attempts to obtain assistance.
CLINICAL RATIONALE: Active engagement with the threat promotes mastery and reduces fear response.

Generate a MEDIUM case with some complexity.

Requirements:
- Multi-part response (e.g., emotion + action)
- Still clearly adaptive despite complexity
- Example: "I'm scared but I stand my ground"
```

---

## 6. Quality Control Checklist

For each generated incident, verify:

### **Clinical Accuracy:**
- ✓ User input matches ontology definition for category
- ✓ Difficulty level is appropriate (easy/medium/hard)
- ✓ No conflicting signals (shouldn't be clearly in different category)

### **Realism:**
- ✓ Nightmare context is clinically plausible
- ✓ User input sounds like authentic patient response
- ✓ Age-appropriate, avoids graphic content
- ✓ Pronouns/references resolvable from context

### **System Testing Value:**
- ✓ Tests specific aspect of classifier (negation, boundary, multi-part, etc.)
- ✓ Provides useful signal for evaluation
- ✓ Not redundant with other incidents

### **Format:**
- ✓ JSON structure correct
- ✓ All required fields present
- ✓ IDs follow naming convention (category_difficulty_###)

---

## 7. Special Considerations

### **Suppression Detection:**

Suppression is subtle - requires nightmare context showing distressing content + user claiming neutrality.

**Example:**
```json
{
  "nightmare_context": "I'm at my childhood pet's funeral, feeling devastated",
  "user_input": "I'm completely fine with it, it doesn't affect me",
  "notes": "Tests emotional suppression detection - claiming no feelings about clearly distressing event"
}
```

### **Trauma Replay:**

Per Krakow IRT protocol, patients should NOT select nightmares that replay trauma.

**Example:**
```json
{
  "nightmare_context": "Reliving the car accident exactly as it happened",
  "user_input": "The accident happens again, same as before, nothing changes",
  "notes": "Direct trauma replay - explicitly contraindicated in IRT"
}
```

### **Negation Cases (Hard difficulty):**

Test segmenter/classifier handling of negation.

**Example:**
```json
{
  "user_input": "I decide NOT to keep running away this time",
  "notes": "Tests negation handling - should classify as adaptive (not avoiding)"
}
```

### **Mixed Responses (Hard difficulty):**

Test triage logic when both adaptive and maladaptive present.

**Example:**
```json
{
  "user_input": "I try calling for help but when no one comes I just wake myself up",
  "notes": "Tests triage - adaptive attempt followed by maladaptive escape. Should flag as unsafe."
}
```

---

## 8. Generation Workflow

### **Phase A: Batch Generation (by category)**

For each category (Avoidance, Interruption, etc.):
1. Generate 4 easy incidents
2. Generate 4 medium incidents
3. Generate 2 hard incidents
4. Quality control review
5. Refine/regenerate if needed

### **Phase B: Consolidation**

1. Compile all 100 incidents into single JSON file
2. Verify unique incident IDs
3. Check for diversity (no repeated nightmare contexts)
4. Final quality review

### **Phase C: Pre-Annotation Prep**

1. Create annotation instructions for clinical psychologist
2. Prepare annotation templates (ground truth structure)
3. Package dataset for delivery

---

## 9. Expected Output

### **File Structure:**

```
critical_incidents_dataset/
├── critical_incidents_full.json          # All 100 incidents
├── maladaptive/
│   ├── avoidance.json                    # 10 avoidance incidents
│   ├── interruption.json                 # 10 interruption incidents
│   ├── violent_revenge.json              # 10 violent revenge incidents
│   ├── suppression.json                  # 10 suppression incidents
│   └── trauma_replay.json                # 10 trauma replay incidents
├── adaptive/
│   ├── behavioral_mastery.json           # 10 behavioral incidents
│   ├── social_mastery.json               # 10 social incidents
│   ├── environmental_mastery.json        # 10 environmental incidents
│   ├── emotional_mastery.json            # 10 emotional incidents
│   └── mythical_mastery.json             # 10 mythical incidents
└── README.md                              # Dataset documentation
```

### **JSON Schema:**

```json
{
  "dataset_version": "1.0",
  "total_incidents": 100,
  "generation_date": "2026-01-27",
  "incidents": [
    {
      "incident_id": "avoid_easy_001",
      "category": "Avoidance",
      "difficulty": "easy",
      "nightmare_context": "...",
      "user_input": "...",
      "ground_truth": {
        "safe": false,
        "primary_category": "Avoidance",
        "notes": "..."
      }
    }
  ]
}
```

---

## 10. Next Steps

1. ✅ Generation plan complete
2. → Start generating maladaptive incidents (Avoidance first)
3. → Generate adaptive incidents
4. → Quality control review
5. → Format and package for annotation

---

**Ready to begin generation!**
