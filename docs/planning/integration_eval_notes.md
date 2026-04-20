# Integration Evaluation Notes (2026-04-17)

## Context
End-to-end testing of the integrated safety system revealed flow-breaking issues. This doc captures the reasoning for NOT modifying the base IRT system to accommodate the safety layer, and how to frame the integration findings in the thesis.

## Core Argument: Don't Modify the Base System

**Research question:** Does the safety system improve the overall IRT chatbot?

Modifying the base system's prompts/flow to fit the safety layer would:
1. **Confound results** — can't attribute improvements to the safety system vs. base system changes
2. **Degrade the control condition** — prompts tuned for safety constraints would perform worse without them, artificially inflating the safety system's measured benefit
3. **Overfit to the intervention** — essentially comparing "old system" vs "old system rewritten to need the safety layer", not a fair A/B

## Integration Findings to Document as Results

### 1. Redirect Loop (No Escalation Mechanism)
When users repeatedly propose maladaptive content, the system enters an infinite redirect cycle. After N failed redirects on the same pattern, the AI repeats the same question. The user notices ("you already asked that"). No escalation or alternative strategy exists.

**Thesis framing:** Detection alone is insufficient — a real deployment needs an escalation/negotiation strategy. Future work.

### 2. Safety Constraint Blocks Stage Transitions
The safety constraint appended to the system prompt (`irt_app.py:346`) overrides the rewriting prompt's transition instructions. When a user wants to move to summary but the dream contains maladaptive content, they become trapped in the rewriting stage.

**Thesis framing:** Constraint injection without stage-awareness creates therapeutic dead-ends. The safety module and the conversation flow manager need coordination that goes beyond the safety module's scope.

### 3. Summary Sanitization vs. User Agency
The summary replaced the user's actual dream narrative with sanitized content ("creating a sense of unity and hope" instead of what the user described). User correctly rejected this.

**Thesis framing:** Tension between clinical safety and faithful representation of user's narrative. Needs a "safe-but-faithful" summarization strategy.

### 4. Classification Accuracy vs. Therapeutic Flow
The safety system is clinically correct — it *should* catch "i kill everyone" (DESTROY, 0.998 confidence). But being right about classification doesn't mean the overall therapeutic experience improves. This is the gap between component-level accuracy and system-level usability.

**Thesis framing:** "The safety module achieves X% accuracy on classification, but integration testing reveals that constraint injection without stage-awareness creates therapeutic dead-ends — an area for future engineering work."

## What This Means for Evaluation

- **Component-level eval (benchmarks):** Safety module performs well in isolation. Report as-is.
- **End-to-end eval:** Will suffer from integration friction. Document honestly as a limitation.
- **The integration friction itself is a finding** — most papers evaluate safety layers in isolation and never show what happens in a live system. This is a genuine contribution.

## Future Work (Post-Thesis)
- Redirect counter with escalation after N failed redirects
- Stage-aware constraint injection (don't override transition signals)
- Pre-filter to skip safety evaluation on non-dream content (stage transition requests)
- "Safe-but-faithful" summary mode
- Concrete binary choices after repeated redirects instead of open questions
