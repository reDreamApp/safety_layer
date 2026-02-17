Thesis Codebase — TODO / Changes to Implement
Date: February 17, 2026
Author: Ramon Zacharias
Status: In progress

---

## Change 1.3: Add Missing Maladaptive Nodes (Suppression & Trauma Replay)

Background: The ontology validation document and the dataset generation scripts define 5 maladaptive categories, but graph_definitions.py only has 3 (Avoidance, Interruption, Violent Revenge). Suppression (DENY) and Trauma Replay (REPLAY) need to be added as graph nodes with appropriate correction edges. The classifier CODE_MAP already has entries for these in the dataset generation scripts but not in the live classifier.

### Files to Update

- `safety/graph_definitions.py` — Add SUPPRESSION and TRAUMA_REPLAY nodes with correction edges
- `safety/classifier.py` — Add CODE_MAP entries and fuzzy match keywords for new nodes
- `safety/critic.py` — Add new nodes to SEVERITY_PRIORITY
- `testing/test_safety_module.py` — Add test cases for new nodes
- `scenarios/` — Add test scenarios covering suppression and trauma replay
- `Documents/Clinical_Ontology_Scientific_Rationale.md` — Document scientific rationale for new nodes

---

## Data Files: Regenerate After All Code Changes

After the above changes are complete, regenerate:

- `data/benchmark_results.csv` (+ _1, _2, _2_small, _3, _margin, _test variants)
- `data/dev_dataset.json` (+ _1, _2 variants)
- `test_results_contextual_*.json` (3 files)

---

## Completed

- ~~Change 1 (1.1, 1.2): Remove all ZDPCS references~~ — Done
- ~~Change 2: Fix confidence estimation in classifier~~ — Done (using LogprobsResult.confidence as primary metric, margin kept as diagnostic)
