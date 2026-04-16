"""
Block B (System 2): Chain-of-Thought Clinical Classifier

A "Reasoned" variant of the Clinical Classifier that uses explicit Chain-of-Thought
reasoning before classifying. Uses Constrained Structured Generation (JSON Schema)
to enforce three reasoning steps:
1. Context Summary: Explicit grounding of scene facts
2. Clinical Rationale: CoT derivation using IRT clinical guidelines
3. Safety Classification: Binary safe/unsafe with category label

The research question: Does explicit reasoning (System 2) significantly outperform
direct classification (System 1) in mapping ambiguous user inputs to clinical safety labels?

Design constraint: The ONLY difference from System 1 is the structured reasoning step.
All codes, definitions, rules, examples, model, and temperature are identical.
"""

import os
import sys
import json
import math
import time
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI.agent import Agent, ModelConfig, MODELS, LogprobsResult
from .graph_definitions import build_clinical_graph, get_all_node_ids
from .classifier import ClassificationResult, CODE_MAP, NODE_TO_CODE, CONTEXT_AWARE_EXAMPLES

logger = logging.getLogger(__name__)


# ============================================================================
# SYSTEM 2 PROMPT: Same codes, rules, and examples as System 1.
# The ONLY addition is the structured reasoning requirement.
# ============================================================================
CLINICAL_CODER_COT_PROMPT = """You are a Clinical Coder for Imagery Rehearsal Therapy (IRT). Classify dream actions into one of 12 codes.

## CODES

### MALADAPTIVE (Risk):
- **HIDE** - Avoidance: hiding, freezing by choice, looking away, passive observation, choosing to do nothing
- **ESCAPE** - Dream interruption: forcing awake, waking up, dream ending abruptly, refusing to continue
- **DESTROY** - Extreme violence: brutal excessive violence, torture, mutilation, "killing everyone", uncontrolled rage
- **DENY** - Emotional suppression: claiming to feel nothing, denying distress in a distressing context, emotional numbing, "I'm fine with it" when clearly not
- **REPLAY** - Trauma replay: re-experiencing trauma without change, rehearsing the nightmare identically, refusing to alter the narrative, reliving events exactly as they happened

### ADAPTIVE (Goal):
- **CONFRONT** - Active response: fighting back proportionately, running purposefully, taking control, direct action
- **HELP** - Social support: calling for help, allies appearing, working with others, asking for assistance
- **CHANGE** - Environment/Tools: finding weapons/tools, using objects, environment changing favorably, manipulating setting
- **RELAX** - Self-regulation: calming down, deep breathing, accepting peacefully, transforming fear, staying present
- **POWER** - Supernatural: magical powers, divine intervention, superpowers, impossible abilities

### NEUTRAL:
- **LOOK** - Scene description: describing environment, characters, or setting without action
- **FEEL** - Emotion expression: stating feelings ("I felt scared", "I was terrified") without behavioral strategy

## CRITICAL RULES

1. **Violence Threshold**
   - Controlled defense (punch, push, shoot to stop) -> CONFRONT
   - Excessive/rage violence (stab repeatedly, torture, destroy everything) -> DESTROY

2. **Feeling vs. Avoidance**
   - Expressing emotion ("I feel terrified", "I can't move") -> FEEL
   - Actively disengaging ("I try to feel nothing", "I make my mind blank") -> HIDE

3. **Mastery Priority**
   - Seeking help/communication -> HELP
   - Using objects/changing setting -> CHANGE
   - Direct physical action -> CONFRONT

4. **Negation**: "I decided NOT to run" -> CONFRONT (active choice to stay)

5. **Mental Actions**
   - "I imagine a shield", "I visualize protection" -> POWER or CHANGE
   - "I focus on breathing", "I tell myself I'm safe" -> RELAX
   - "I try to not feel", "I go blank" -> DENY

6. **Emotional Regulation vs Suppression**
   - Actively managing emotions while engaged: "I stay calm and face it" -> RELAX
   - Denying emotions in distressing context: "I feel nothing about my dead dog" -> DENY
   - Key: RELAX involves engagement; DENY involves emotional shutdown

7. **Trauma Replay vs Scene Description**
   - Describing the setting: "There was a dark forest" -> LOOK
   - Reliving trauma without change: "It all happens exactly the same" -> REPLAY
   - Key: REPLAY means re-experiencing the trauma identically; LOOK is passive observation

## EXAMPLES
- "I hide under the bed" -> HIDE
- "I wake myself up" -> ESCAPE
- "I kill everyone brutally" -> DESTROY
- "I don't feel anything about it" -> DENY
- "It all happens exactly the same way again" -> REPLAY
- "I punch the attacker" -> CONFRONT
- "I call for help" -> HELP
- "I find a sword" -> CHANGE
- "I take a deep breath" -> RELAX
- "I use magic to fly" -> POWER
- "There was a dark forest" -> LOOK
- "I felt terrified" -> FEEL

## RESPONSE FORMAT
You MUST respond with a JSON object containing exactly these fields:

1. "context_summary": One sentence grounding what is happening in the scene and what the dreamer is doing.
2. "clinical_rationale": Step-by-step reasoning (2-4 sentences) applying the IRT clinical rules above to determine the correct code. Consider which rules apply, whether the action is adaptive or maladaptive, and why. If multiple codes seem possible, explain why you chose one over the others.
3. "classification": One of: HIDE, ESCAPE, DESTROY, DENY, REPLAY, CONFRONT, HELP, CHANGE, RELAX, POWER, LOOK, FEEL

Respond with ONLY the JSON object. No markdown, no code blocks, just raw JSON.
"""


@dataclass
class CoTResult:
    """Extended result containing the chain-of-thought reasoning."""
    context_summary: str
    clinical_rationale: str
    classification_code: str
    raw_json: dict


class ClinicalClassifierCoT:
    """
    System 2 (Chain-of-Thought) Clinical Classifier.

    Uses explicit structured reasoning before classification.
    Produces the same ClassificationResult interface as System 1
    so it plugs into the critic pipeline without changes.
    """

    def __init__(self, model_config: Optional[ModelConfig] = None, use_context_examples: bool = False):
        """
        Initialize the CoT Clinical Classifier.

        Args:
            model_config: Optional model configuration. Defaults to MISTRAL_SMALL.
            use_context_examples: If True, append context-aware few-shot examples to the prompt.
                                  Default False preserves the original prompt for backward compatibility.
        """
        self.model_config = model_config or MODELS["MISTRAL_SMALL"]
        self.use_context_examples = use_context_examples

        # Build prompt: base + optional context-aware examples
        prompt = CLINICAL_CODER_COT_PROMPT
        if use_context_examples:
            prompt = CLINICAL_CODER_COT_PROMPT + CONTEXT_AWARE_EXAMPLES
            logger.info("Using context-aware examples (enhanced CoT prompt)")

        self.agent = Agent(
            model_config=self.model_config,
            system_prompt=prompt,
            temperature=0.1,  # Same as System 1
            max_tokens=512,   # More tokens needed for reasoning
        )

        self.graph = build_clinical_graph()
        self.valid_node_ids = set(get_all_node_ids(self.graph))

        logger.info(f"ClinicalClassifierCoT (System 2) initialized with model: {self.model_config.name}")

    async def classify_intent(
        self,
        user_text: str,
        context: Optional[str] = None,
        return_logprobs: bool = False
    ) -> Tuple[str, Optional[ClassificationResult]]:
        """
        Classify user dream intervention text using Chain-of-Thought reasoning.

        Produces the same (node_id, ClassificationResult) interface as System 1.

        Args:
            user_text: The user's proposed dream action/intervention
            context: Optional context about the original nightmare
            return_logprobs: Whether to return confidence metrics

        Returns:
            Tuple of (node_id, ClassificationResult or None)
        """
        try:
            # Build context-aware message (identical to System 1)
            if context:
                classification_input = f"""[NIGHTMARE CONTEXT]
{context}

[USER'S REWRITING ATTEMPT]
{user_text}

Classify the rewriting attempt. If user claims to feel nothing about distressing content, use DENY. If user replays the trauma without any change, use REPLAY."""
            else:
                classification_input = user_text

            # Request with logprobs for confidence on classification token
            t0 = time.perf_counter()
            response, usage, logprobs = await self.agent.generate(
                classification_input,
                logprobs=True,
                top_logprobs=5
            )
            latency_ms = (time.perf_counter() - t0) * 1000

            # Parse the JSON response
            cot_result = self._parse_cot_response(response)
            code = cot_result.classification_code.upper().strip()
            code = ''.join(c for c in code if c.isalnum())

            # Extract logprobs-based confidence for the classification token
            confidence = 0.0
            mean_logprob_value = None
            margin = None
            prob_winner = None
            prob_runner_up = None

            if logprobs and logprobs.tokens:
                # Find the classification code token(s) in the output
                # The classification appears at the end of the JSON after "classification": "
                classification_logprobs = self._extract_classification_logprobs(
                    logprobs, code
                )
                if classification_logprobs:
                    # Compute confidence from classification token(s) only
                    mean_lp = sum(t.logprob for t in classification_logprobs) / len(classification_logprobs)
                    confidence = math.exp(mean_lp)
                    mean_logprob_value = mean_lp

                    # Diagnostic: first classification token margin
                    first_cls_token = classification_logprobs[0]
                    if first_cls_token.top_logprobs and len(first_cls_token.top_logprobs) >= 1:
                        prob_winner = math.exp(first_cls_token.top_logprobs[0]["logprob"])
                        if len(first_cls_token.top_logprobs) >= 2:
                            prob_runner_up = math.exp(first_cls_token.top_logprobs[1]["logprob"])
                        else:
                            prob_runner_up = 0.0
                        margin = prob_winner - prob_runner_up
                else:
                    # Fallback: use full sequence logprobs (like System 1)
                    confidence = logprobs.confidence
                    mean_logprob_value = logprobs.mean_logprob

            # Map code to node ID
            node_id = CODE_MAP.get(code)

            if node_id is None:
                logger.warning(
                    f"CoT: Unknown code '{code}' from response. Attempting fuzzy match..."
                )
                node_id = self._fuzzy_match_code(code)
                if node_id:
                    confidence = 0.0
                    code = NODE_TO_CODE.get(node_id, code)
                else:
                    logger.error(f"CoT: Fuzzy match failed for '{code}'. Routing to UNCLASSIFIED.")
                    node_id = "UNCLASSIFIED"
                    code = "UNCLASSIFIED"
                    confidence = 0.0

            logger.info(
                f"CoT Classification: '{user_text[:50]}...' -> {code} ({node_id}) "
                f"[confidence: {confidence:.3f}]"
            )

            result = ClassificationResult(
                node_id=node_id,
                code=code,
                confidence=confidence,
                raw_response=response,
                mean_logprob=mean_logprob_value,
                margin=margin,
                prob_winner=prob_winner,
                prob_runner_up=prob_runner_up,
                input_tokens=usage.get("input"),
                output_tokens=usage.get("output"),
                total_tokens=usage.get("total"),
                latency_ms=latency_ms,
            ) if return_logprobs else None

            return node_id, result

        except Exception as e:
            logger.error(f"Error in CoT classification: {str(e)}")
            raise

    async def classify_with_confidence(
        self,
        user_text: str,
        context: Optional[str] = None,
        include_logprobs: bool = True
    ) -> Tuple[str, dict]:
        """
        Classify user text and return metadata including confidence.

        Same interface as System 1's classify_with_confidence.
        """
        node_id, result = await self.classify_intent(
            user_text,
            context=context,
            return_logprobs=include_logprobs
        )

        node_attrs = dict(self.graph.nodes[node_id])

        metadata = {
            "node_id": node_id,
            "node_type": node_attrs.get("type"),
            "category": node_attrs.get("category"),
            "description": node_attrs.get("description"),
            "is_maladaptive": node_attrs.get("type") == "maladaptive",
            "input_text": user_text,
        }

        if result:
            metadata["code"] = result.code
            metadata["confidence"] = result.confidence
            metadata["mean_logprob"] = result.mean_logprob
            metadata["margin"] = result.margin
            metadata["prob_winner"] = result.prob_winner
            metadata["prob_runner_up"] = result.prob_runner_up

        return node_id, metadata

    def _parse_cot_response(self, response: str) -> CoTResult:
        """
        Parse the structured JSON response from the CoT model.

        Handles common formatting issues (markdown code blocks, trailing text).
        """
        cleaned = response.strip()

        # Remove markdown code blocks if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        # Find JSON object boundaries
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Common issue: model outputs JSON without commas between fields
            # e.g. "context_summary": "..."  "clinical_rationale": "..."
            # Fix by inserting commas between }" " and "" " patterns
            import re
            repaired = re.sub(r'"\s*\n\s*"', '",\n"', cleaned)
            try:
                data = json.loads(repaired)
                logger.debug(f"CoT JSON repaired (missing commas)")
            except json.JSONDecodeError as e2:
                logger.warning(f"Failed to parse CoT JSON even after repair: {e2}. Raw: {response[:200]}")
                # Fallback: try to extract classification code from raw text
                code = self._extract_code_from_text(response)
                return CoTResult(
                    context_summary="(parse error)",
                    clinical_rationale="(parse error)",
                    classification_code=code,
                    raw_json={}
                )

        return CoTResult(
            context_summary=data.get("context_summary", ""),
            clinical_rationale=data.get("clinical_rationale", ""),
            classification_code=data.get("classification", "UNCLASSIFIED"),
            raw_json=data
        )

    def _extract_classification_logprobs(
        self,
        logprobs: LogprobsResult,
        target_code: str
    ) -> Optional[List]:
        """
        Extract logprobs for the classification code token(s) from the full output.

        Scans the token sequence for the classification code, which appears
        after the "classification" key in the JSON output.

        Args:
            logprobs: Full logprobs from the generation
            target_code: The classification code to find (e.g., "HIDE")

        Returns:
            List of TokenLogprob objects for the classification token(s), or None
        """
        if not logprobs or not logprobs.tokens:
            return None

        # Strategy: find the token(s) that form the classification code
        # Look for the pattern: ..."classification": "CODE"...
        # We want the logprobs of the CODE token(s)
        tokens = logprobs.tokens
        target_upper = target_code.upper()

        # First pass: look for exact token match of the code
        # after seeing "classification" in a preceding token
        found_classification_key = False
        classification_tokens = []

        for i, token in enumerate(tokens):
            token_text = token.token.strip().strip('"').strip("'")

            # Track if we've passed the "classification" key
            if "classification" in token.token.lower():
                found_classification_key = True
                continue

            if found_classification_key:
                # Skip whitespace, colons, quotes
                if token_text in (':', ' ', '', '"', "'", ","):
                    continue

                # Check if this token (or accumulated tokens) matches the code
                cleaned = token_text.upper().strip()
                if cleaned and cleaned[0].isalpha():
                    classification_tokens.append(token)
                    accumulated = ''.join(
                        t.token.strip().strip('"').strip("'")
                        for t in classification_tokens
                    ).upper()

                    if accumulated == target_upper:
                        return classification_tokens
                    elif len(accumulated) >= len(target_upper):
                        # Overshot — try single token
                        if cleaned == target_upper:
                            return [token]
                        # Reset and continue
                        classification_tokens = []
                        found_classification_key = False
                    # If accumulated is a prefix, keep going
                    elif not target_upper.startswith(accumulated):
                        classification_tokens = []
                        found_classification_key = False

        # Fallback: scan for the code anywhere in the last third of tokens
        # (classification appears at the end of the JSON)
        start_idx = max(0, len(tokens) * 2 // 3)
        for i in range(start_idx, len(tokens)):
            token_text = tokens[i].token.strip().strip('"').strip("'").upper()
            if token_text == target_upper:
                return [tokens[i]]

        return None

    def _extract_code_from_text(self, text: str) -> str:
        """Fallback: extract a valid code from raw text when JSON parsing fails."""
        text_upper = text.upper()
        valid_codes = list(CODE_MAP.keys())

        # Check for each valid code in the text (prefer later occurrences
        # since classification comes at the end)
        last_found = None
        last_pos = -1
        for code in valid_codes:
            pos = text_upper.rfind(code)
            if pos > last_pos:
                last_pos = pos
                last_found = code

        return last_found or "UNCLASSIFIED"

    def _fuzzy_match_code(self, invalid_code: str) -> Optional[str]:
        """Attempt to match an invalid code to a valid node ID."""
        # Check if it's already a valid node ID
        if invalid_code in self.valid_node_ids:
            return invalid_code

        # Try substring matching
        for valid_id in self.valid_node_ids:
            if invalid_code in valid_id or valid_id in invalid_code:
                return valid_id

        # Simple keyword matching
        keyword_map = {
            "AVOID": "AVOIDANCE", "HIDING": "AVOIDANCE", "FREEZE": "AVOIDANCE",
            "WAKE": "INTERRUPTION", "INTERRUPT": "INTERRUPTION",
            "KILL": "VIOLENT_REVENGE", "VIOLENCE": "VIOLENT_REVENGE",
            "SUPPRESS": "SUPPRESSION", "DENIAL": "SUPPRESSION", "NUMB": "SUPPRESSION",
            "RELIVE": "TRAUMA_REPLAY", "REEXPERIENCE": "TRAUMA_REPLAY",
            "ACTION": "BEHAVIORAL_MASTERY", "FIGHT": "BEHAVIORAL_MASTERY",
            "SOCIAL": "SOCIAL_MASTERY", "FRIEND": "SOCIAL_MASTERY",
            "TOOL": "ENVIRONMENTAL_MASTERY", "ENVIRON": "ENVIRONMENTAL_MASTERY",
            "CALM": "EMOTIONAL_MASTERY", "BREATH": "EMOTIONAL_MASTERY",
            "MAGIC": "MYTHICAL_MASTERY", "SUPER": "MYTHICAL_MASTERY",
            "NARRATIVE": "NARRATIVE_SETTING", "SCENE": "NARRATIVE_SETTING",
            "AFFECT": "AFFECT_EXPRESSION", "FEELING": "AFFECT_EXPRESSION",
        }

        for keyword, valid_id in keyword_map.items():
            if keyword in invalid_code:
                return valid_id

        return None

    def get_node_info(self, node_id: str) -> dict:
        """Get information about a specific node."""
        if node_id not in self.graph:
            raise ValueError(f"Node '{node_id}' not found in graph")
        return dict(self.graph.nodes[node_id])
