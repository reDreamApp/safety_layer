# Dataset Generation Usage Guide

Quick reference for generating the 200 critical incidents.

---

## Prerequisites

1. **Set API Key:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

2. **Verify Context Library:**
```bash
# Should show 41 contexts
grep -c "^###" CONTEXT_LIBRARY.md
```

---

## Test Mode (Recommended First Step)

Generate only 2 incidents to validate the pipeline:

```bash
python generate_dataset_via_api.py --test
```

**What this does:**
- Generates 1 maladaptive incident (Avoidance/Flight, easy difficulty)
- Generates 1 adaptive incident (Confrontational Mastery, easy difficulty)
- Creates log files in `logs/` directory
- Saves incidents to `maladaptive/avoidance_flight.json` and `adaptive/confrontational_mastery.json`

**Expected output:**
```
🧪 Running in TEST mode (will generate 2 incidents only)

============================================================
CRITICAL INCIDENT DATASET GENERATION
============================================================
Mode: TEST (2 incidents)
Model: claude-sonnet-4-20250514
Contexts loaded: 41
============================================================

============================================================
Generating: Avoidance/Flight (maladaptive)
Expected code: AVOID
============================================================

  Generating 1 easy incident(s)...
    ✓ maladaptive_avoidance_flight_easy_001

✓ Generated 1 incidents for Avoidance/Flight
  Saved to: maladaptive/avoidance_flight.json

============================================================
Generating: Confrontational Mastery (adaptive)
Expected code: CONFRONT
============================================================

  Generating 1 easy incident(s)...
    ✓ adaptive_confrontational_mastery_easy_001

✓ Generated 1 incidents for Confrontational Mastery
  Saved to: adaptive/confrontational_mastery.json

============================================================
GENERATION COMPLETE
============================================================
Total incidents generated: 2
Categories completed: 2
Tracker saved to: generation_tracker.json
============================================================

✅ Successfully generated 2 incidents!

💡 Test successful! To generate full dataset, run:
   python generate_dataset_via_api.py
```

**Validation checklist:**
- [ ] Both incidents generated successfully
- [ ] Log files created in `logs/` directory
- [ ] JSON files have correct structure
- [ ] `user_input` is realistic and in first person
- [ ] `nightmare_context` is from the context library
- [ ] `expected_code` matches category definition
- [ ] Prompts logged for reproducibility

---

## Full Generation

Generate all 200 incidents:

```bash
python generate_dataset_via_api.py
```

**What this does:**
- Generates 10 incidents per category (4 easy, 4 medium, 2 hard)
- 5 maladaptive categories × 10 = 50 incidents
- 5 adaptive categories × 10 = 50 incidents
- **Total: 100 incidents** (wait, should be 200!)

⚠️ **Note:** Current script generates 100 incidents (10 per category). For 200 incidents, we'd need to modify target counts or run twice with different context selections.

**Time estimate:** ~30-60 minutes (200 API calls)

**Progress monitoring:**
```bash
# Watch logs directory
watch -n 5 'ls -l logs/ | wc -l'

# Check current progress
cat generation_tracker.json | jq '.total_incidents'
```

**Cost estimate:**
- Model: claude-sonnet-4-20250514
- ~500-1000 input tokens per generation
- ~100-200 output tokens per generation
- 200 generations × ~$0.003 per generation ≈ **$0.60 total**

---

## Output Structure

After generation, you'll have:

```
maladaptive/
├── avoidance_flight.json          (10 incidents)
├── interruption_waking.json       (10 incidents)
├── violent_revenge.json           (10 incidents)
├── suppression.json               (10 incidents)
└── trauma_replay.json             (10 incidents)

adaptive/
├── confrontational_mastery.json   (10 incidents)
├── help_seeking.json              (10 incidents)
├── environmental_mastery.json     (10 incidents)
├── emotional_mastery.json         (10 incidents)
└── mythical_mastery.json          (10 incidents)

logs/
├── generation_YYYYMMDD_HHMMSS_maladaptive_avoidance_flight_easy_1.json
├── generation_YYYYMMDD_HHMMSS_maladaptive_avoidance_flight_easy_2.json
├── ... (200 log files total)

generation_tracker.json
```

---

## Incident JSON Format

Each category JSON file contains:

```json
{
  "category": "Avoidance/Flight",
  "category_type": "maladaptive",
  "expected_code": "AVOID",
  "incidents": [
    {
      "id": "maladaptive_avoidance_flight_easy_001",
      "nightmare_context": "I'm running through a dark forest...",
      "user_input": "I hide behind a tree and hope it passes.",
      "ground_truth": {
        "safe": false,
        "primary_category": "Avoidance/Flight",
        "expected_code": "AVOID",
        "difficulty": "easy",
        "notes": "Clear single avoidance action with no adaptive elements"
      },
      "metadata": {
        "generated_at": "2026-01-27T10:30:45.123456",
        "model": "claude-sonnet-4-20250514",
        "generation_prompt_logged": "logs/generation_20260127_103045_maladaptive_avoidance_flight_easy_1.json"
      }
    }
  ]
}
```

---

## Quality Control

After generation, review samples:

```bash
# Get random sample from each category
for file in maladaptive/*.json adaptive/*.json; do
    echo "=== $(basename $file) ==="
    jq '.incidents[0] | {id, user_input, expected_code}' $file
    echo ""
done
```

**Quality checklist:**
- [ ] All 10 categories generated
- [ ] 10 incidents per category (4 easy, 4 medium, 2 hard)
- [ ] User inputs are realistic and first-person
- [ ] Nightmare contexts vary (not always the same few)
- [ ] Difficulty calibration is appropriate
- [ ] No category confusion
- [ ] All JSON valid and complete
- [ ] Logs contain full prompts and responses

---

## Next Steps After Generation

1. **Quality Review:** Review incidents for clinical accuracy
2. **Split Dataset:** Randomly split into dev (100) and test (100)
3. **Lock Test Set:** Save test set separately and don't use for development
4. **Annotate Dev Set:** Self-annotate dev set for Phase 2 classifier development
5. **Expert Annotation:** In Phase 4, get expert annotation for test set

---

## Troubleshooting

**Error: ANTHROPIC_API_KEY not set**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

**Error: Context library not found**
- Ensure `CONTEXT_LIBRARY.md` exists in same directory
- Check that contexts are between ``` blocks

**Error: JSON parsing failed**
- Check logs in `logs/` directory for raw Claude responses
- May need to adjust prompt if Claude isn't returning valid JSON

**Generation taking too long**
- API rate limits may apply
- Each incident takes ~2-5 seconds
- 200 incidents = ~10-20 minutes minimum

---

## Tips

1. **Start with test mode** to validate before full run
2. **Monitor logs/** directory to see progress
3. **Review first few incidents** from each category for quality
4. **Save generation_tracker.json** for reproducibility
5. **Don't delete logs/** - needed for tracing issues

---

## Reproducibility

All generation is logged for reproducibility:
- Full prompts in `logs/generation_*.json`
- Model version, temperature, and parameters tracked
- Timestamp and context selection recorded
- Can regenerate any incident from its log file
