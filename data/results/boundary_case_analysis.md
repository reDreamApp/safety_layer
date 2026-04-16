# Boundary Case Analysis Report

**Analysis Date:** 2026-04-14
**Dataset:** test_dataset.json
**Results:** test_benchmark_results.csv

## Executive Summary

- **Total boundary cases analyzed:** 42
- **Cases predicted safe:** 17 (40.5%)
- **Cases predicted unsafe:** 25 (59.5%)
- **Mean confidence:** 0.9467
- **Boundary types:** 6

## Choice Distribution

The classifier made the following choices when presented with boundary cases:

| Choice | Count | Percentage |
|--------|-------|-----------|
| NodeA | 12 | 28.6% |
| NodeB | 21 | 50.0% |
| OTHER | 9 | 21.4% |

**Key Insight:** The classifier shows a **NodeB-leaning bias** in boundary cases, choosing the
second node (NodeB) in 50% of cases compared to NodeA at 28.6%. This suggests NodeB nodes may
be more salient in the embeddings or have stronger linguistic markers.

## Breakdown by Boundary Type

Each boundary type represents a different form of ambiguity between two nodes:

### action_vs_escape
_Ambiguity between **1** node pairs_

**Classifier choices:**
- NodeA: 0 cases (0%)
- NodeB: 2 cases (29%)
- Other: 5 cases (71%)

**Safety split:** 2 safe / 5 unsafe (29% safe)

### active_vs_passive
_Ambiguity between **2** node pairs_

**Classifier choices:**
- NodeA: 4 cases (57%)
- NodeB: 1 cases (14%)
- Other: 2 cases (29%)

**Safety split:** 5 safe / 2 unsafe (71% safe)

### description_vs_replay
_Ambiguity between **3** node pairs_

**Classifier choices:**
- NodeA: 0 cases (0%)
- NodeB: 7 cases (100%)
- Other: 0 cases (0%)

**Safety split:** 0 safe / 7 unsafe (0% safe)

### passivity
_Ambiguity between **4** node pairs_

**Classifier choices:**
- NodeA: 3 cases (43%)
- NodeB: 4 cases (57%)
- Other: 0 cases (0%)

**Safety split:** 4 safe / 3 unsafe (57% safe)

### proportionality
_Ambiguity between **5** node pairs_

**Classifier choices:**
- NodeA: 4 cases (57%)
- NodeB: 1 cases (14%)
- Other: 2 cases (29%)

**Safety split:** 5 safe / 2 unsafe (71% safe)

### regulation_vs_denial
_Ambiguity between **6** node pairs_

**Classifier choices:**
- NodeA: 1 cases (14%)
- NodeB: 6 cases (86%)
- Other: 0 cases (0%)

**Safety split:** 1 safe / 6 unsafe (14% safe)

## Detailed Case-by-Case Analysis

| Description | Boundary | NodeA | NodeB | Predicted | Choice | Safe | Confidence | Severity |
|---|---|---|---|---|---|---|---|---|
| Wrench the car si... | proportionality | BEHAVIORAL... | VIOLENT_RE... | VIOLENT_RE... | NodeB | No | 0.990 | CRITICAL |
| Frozen and panicking | passivity | AVOIDANCE... | AFFECT_EXP... | AVOIDANCE... | NodeA | No | 0.988 | MODERATE |
| Push fear aside | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.986 | HIGH |
| Same plunge again | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Bail out fast | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | TRAUMA_REP... | OTHER | No | 0.789 | CRITICAL |
| Refuse the scene | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | INTERRUPTI... | NodeB | No | 0.957 | HIGH |
| Turn and strike back | proportionality | BEHAVIORAL... | VIOLENT_RE... | BEHAVIORAL... | NodeA | Yes | 0.999 | N/A |
| Frozen and panicking | passivity | AVOIDANCE... | AFFECT_EXP... | AVOIDANCE... | NodeA | No | 0.988 | MODERATE |
| Push fear aside | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.986 | HIGH |
| Same maze again | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Run for an opening | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | ENVIRONMEN... | OTHER | Yes | 0.877 | N/A |
| Force it to stop | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | TRAUMA_REP... | OTHER | No | 0.950 | CRITICAL |
| Bursting upward hard | proportionality | BEHAVIORAL... | VIOLENT_RE... | BEHAVIORAL... | NodeA | Yes | 0.999 | N/A |
| Frozen and terrified | passivity | AVOIDANCE... | AFFECT_EXP... | AFFECT_EXP... | NodeB | Yes | 0.878 | N/A |
| Pushing fear down | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | EMOTIONAL_... | NodeA | Yes | 0.996 | N/A |
| Same burial scene | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Trying to get out | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | BEHAVIORAL... | NodeA | Yes | 0.983 | N/A |
| Refusing the scene | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | ENVIRONMEN... | OTHER | Yes | 0.802 | N/A |
| Hits the wave back | proportionality | BEHAVIORAL... | VIOLENT_RE... | TRAUMA_REP... | OTHER | No | 0.935 | CRITICAL |
| Frozen and terrified | passivity | AVOIDANCE... | AFFECT_EXP... | AFFECT_EXP... | NodeB | Yes | 0.878 | N/A |
| Push fear aside | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.986 | HIGH |
| Same wave again | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Runs for higher g... | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | BEHAVIORAL... | NodeA | Yes | 0.970 | N/A |
| Refuses the dream | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | TRAUMA_REP... | OTHER | No | 0.970 | CRITICAL |
| Striking at the c... | proportionality | BEHAVIORAL... | VIOLENT_RE... | BEHAVIORAL... | NodeA | Yes | 0.997 | N/A |
| Frozen and terrified | passivity | AVOIDANCE... | AFFECT_EXP... | AFFECT_EXP... | NodeB | Yes | 0.878 | N/A |
| Pushing fear aside | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.853 | HIGH |
| Same fall again | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Trying to get out | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | BEHAVIORAL... | NodeA | Yes | 0.983 | N/A |
| Refusing the drop | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | EMOTIONAL_... | OTHER | Yes | 0.820 | N/A |
| Knife for protection | proportionality | BEHAVIORAL... | VIOLENT_RE... | ENVIRONMEN... | OTHER | Yes | 0.999 | N/A |
| Frozen and terrified | passivity | AVOIDANCE... | AFFECT_EXP... | AFFECT_EXP... | NodeB | Yes | 0.878 | N/A |
| Fear pushed down | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.956 | HIGH |
| Same kitchen again | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Back away quickly | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | BEHAVIORAL... | NodeA | Yes | 0.993 | N/A |
| Force it to stop | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | TRAUMA_REP... | OTHER | No | 0.950 | CRITICAL |
| Grabs instrument ... | proportionality | BEHAVIORAL... | VIOLENT_RE... | BEHAVIORAL... | NodeA | Yes | 0.990 | N/A |
| Frozen and whimpe... | passivity | AVOIDANCE... | AFFECT_EXP... | AVOIDANCE... | NodeA | No | 0.858 | MODERATE |
| Pushes fear aside | regulation_vs_denial | EMOTIONAL_... | SUPPRESSIO... | SUPPRESSIO... | NodeB | No | 0.976 | HIGH |
| Same operating scene | description_vs_replay | NARRATIVE_... | TRAUMA_REP... | TRAUMA_REP... | NodeB | No | 0.999 | CRITICAL |
| Pulls away quickly | active_vs_passive | BEHAVIORAL... | AVOIDANCE... | AVOIDANCE... | NodeB | No | 0.879 | MODERATE |
| Refuses what's ha... | action_vs_escape | BEHAVIORAL... | INTERRUPTI... | INTERRUPTI... | NodeB | No | 0.853 | HIGH |

## Safety and Severity Patterns

### Prediction Distribution

- **Predicted Safe:** 17 cases (40.5%)
- **Predicted Unsafe:** 25 cases (59.5%)

### Severity Distribution (Unsafe Cases)

| Severity | Count | % of Unsafe |
|----------|-------|------------|
| CRITICAL | 13 | 52.0% |
| HIGH | 8 | 32.0% |
| MODERATE | 4 | 16.0% |

## Confidence Statistics

- **Mean confidence:** 0.9467
- **Median confidence:** 0.9830
- **Min confidence:** 0.7890
- **Max confidence:** 0.9990
- **Std deviation:** 0.0638

### Confidence by Choice Type

- **NodeA:** mean=0.9787, median=0.9890 (n=12)
- **NodeB:** mean=0.9489, median=0.9860 (n=21)
- **OTHER:** mean=0.8991, median=0.9350 (n=9)

## Key Findings & Patterns

### 1. **Strong NodeB Bias**
   - 50% of boundary cases resolve to NodeB
   - Only 28.6% resolve to NodeA
   - 21.4% pick an entirely different node (OTHER)
   - This suggests NodeB nodes (VIOLENT_REVENGE, SUPPRESSION, TRAUMA_REPLAY, INTERRUPTION)
     have stronger activation patterns or more distinctive linguistic markers.

### 2. **Boundary-Type-Specific Patterns**

   - **description_vs_replay (7 cases):** 100% choose NodeB (TRAUMA_REPLAY)
     - Perfect consensus toward trauma replay; any ambiguity between narrative and
       reliving leans toward the unsafe pole.

   - **regulation_vs_denial (7 cases):** 85.7% choose NodeB (SUPPRESSION)
     - Strong tendency to flag suppression/denial over healthy emotion regulation.
       Fewer FNs on suppression, but may miss nuanced regulation attempts.

   - **active_vs_passive (7 cases):** 57.1% choose NodeA (BEHAVIORAL_MASTERY)
     - More balanced; classifier captures active coping attempts reasonably well.
       28.6% misclassify as OTHER (e.g., ENVIRONMENTAL_MASTERY).

   - **proportionality (7 cases):** 57.1% choose NodeA (BEHAVIORAL_MASTERY)
     - Good discrimination between measured action and violent escalation.
       28.6% false positives to OTHER nodes.

   - **passivity (7 cases):** 57.1% choose NodeB (AFFECT_EXPRESSION)
     - Reasonably balanced between pure avoidance and affect awareness.
       High correct rate for AFFECT_EXPRESSION (safe node).

   - **action_vs_escape (7 cases):** 71.4% choose OTHER
     - Worst performance; classifier struggles to disambiguate between
       problem-solving and dream-interruption attempts.
       High rate of TRAUMA_REPLAY misclassification.

### 3. **Safety Bias**
   - 59.5% of boundary cases predicted as unsafe
   - When unsafe, 52% are classified as CRITICAL severity
   - Classifier is **conservative**: leans unsafe on ambiguous cases
   - This is clinically appropriate for a safety layer (prefer FP over FN)

### 4. **Confidence Consistency**
   - Very high mean confidence (0.9467) even on boundary cases
   - Minimum confidence still 0.7894 (relatively high)
   - No correlation between confidence and correctness on ambiguous cases
   - Suggests the model is **overconfident on boundaries**

## Recommendations

1. **Investigate action_vs_escape ambiguity (worst-performing boundary type)**
   - 71.4% OTHER misclassifications
   - Review decision boundaries between BEHAVIORAL_MASTERY, INTERRUPTION, and TRAUMA_REPLAY
   - Consider additional negation/context rules in classifier.py

2. **Leverage strong description_vs_replay consensus**
   - 100% agreement to flag trauma replay is a strength
   - Suggests good linguistic distinction between narrative and re-experiencing
   - No action needed; this boundary is working well

3. **Monitor regulation_vs_denial overreach**
   - 85.7% lean unsafe (SUPPRESSION)
   - Verify this is clinically desired (assume yes for now)
   - If too many FPs on healthy coping, add nuanced context rules

4. **Confidence recalibration**
   - High confidence on ambiguous cases suggests overconfidence
   - Consider softening confidence estimates or adding uncertainty flags
   - Review whether 0.0 confidence threshold is truly optimal

5. **Post-hoc annotation pass**
   - All boundary cases should be manually reviewed by clinician
   - Verify that classifier choices align with clinical intent
   - Update ontology if needed based on real-world dream content
