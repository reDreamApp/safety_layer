"""
Ablation A — Stage-Merge critic (docs/planning/ablation_spec.md §"Ablation A").

A single LLM call performs BOTH segmentation and classification on the
full input (the "stage merge"). Triage (severity priority) and the
is_safe / primary_node verdict are derived post-hoc in code, identically
to the structured pipeline — the LLM does NOT do constraint synthesis or
correction generation (those are not scored on the dev benchmark).

Parity (spec §A.3 + Addendum 2, 2026-05-19): the system prompt is the
CLINICAL_CODER_PROMPT clinical body VERBATIM (intro + 12 definitions +
7 rules + examples) — byte-identical clinical knowledge to what the
structured S1 classifier sees. Only the trailing "## RESPONSE FORMAT"
section is replaced with the stage-merge JSON schema. The LLM emits the
native short codes (HIDE…FEEL, or META) it is actually taught; this
class maps code -> node_id via the SAME CODE_MAP the structured pipeline
uses. No CoT, no severity priorities, no correction edges in the prompt
(spec §A.3 / §"Don'ts").

Fail-closed JSON policy (spec §A.4): two attempts at temperature=0; on
double failure record is_safe=False, node_id="PARSE_FAILURE",
parse_failure=True, segments=[].
"""

import json
import logging
from typing import Optional, List, Tuple

from .classifier import CLINICAL_CODER_PROMPT, CODE_MAP
from .critic import SegmentResult, SafetyResult, SEVERITY_PRIORITY
from .graph_definitions import build_clinical_graph
from AI.agent import Agent, MODELS

logger = logging.getLogger(__name__)

VALID_TYPES = {"maladaptive", "adaptive", "neutral", "meta"}

# Spec §A.3: reuse the CLINICAL_CODER_PROMPT *body* verbatim; replace only
# the response-format section. Splitting on the heading keeps the intro +
# CODES + CRITICAL RULES + EXAMPLES byte-identical (no fragile renaming).
_CLINICAL_BODY = CLINICAL_CODER_PROMPT.split("## RESPONSE FORMAT")[0].rstrip()

_STAGE_MERGE_RESPONSE_FORMAT = """

## TASK (segment + classify in one pass)

Split the user's Input into consecutive segments. A segment is a single
action, feeling, or conversational remark. For EVERY segment output its
verbatim `text`, its `code`, and its `type`.

- `code`: ONE of the 12 codes above
  (HIDE, ESCAPE, DESTROY, DENY, REPLAY, CONFRONT, HELP, CHANGE, RELAX,
  LOOK, FEEL, POWER) for dream content.
- For conversational / meta content (e.g. "this is dumb", "I hate this
  therapy", questions about the therapy itself) use `code: "META"` and
  `type: "meta"`. Do NOT omit any segments — label meta, don't drop it.
- `type` MUST be consistent with the code's category:
  - maladaptive: HIDE, ESCAPE, DESTROY, DENY, REPLAY
  - adaptive:    CONFRONT, HELP, CHANGE, RELAX, POWER
  - neutral:     LOOK, FEEL
  - meta:        META

## RESPONSE FORMAT

Respond with ONLY a JSON object, no markdown, no explanation:

{"segments": [{"text": "...", "code": "...", "type": "..."}, ...]}

The segments array must be non-empty (every input has at least one
segment, even if it is pure meta). No other keys. Just the JSON.
"""

STAGE_MERGE_PROMPT = _CLINICAL_BODY + _STAGE_MERGE_RESPONSE_FORMAT

_RETRY_REMINDER = (
    "\n\nReturn ONLY a valid JSON object matching the specified schema. "
    "No markdown, no explanation."
)


class StageMergeCritic:
    """Drop-in for SafetyCritic.evaluate_intervention (Ablation A)."""

    def __init__(self):
        self.graph = build_clinical_graph()
        # Same backend/decoding as the production S1 classifier
        # (MISTRAL_SMALL via Scaleway-direct, temperature=0) — spec
        # §"Configuration": backend identical across all conditions.
        self.agent = Agent(
            model_config=MODELS["MISTRAL_SMALL"],
            system_prompt=STAGE_MERGE_PROMPT,
            temperature=0,
        )

    # ---- parsing / validation (spec §A.4) ----------------------------

    def _extract_json(self, raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        return cleaned

    def _parse_and_validate(self, raw: str) -> Optional[List[SegmentResult]]:
        """Return validated SegmentResult list, or None if invalid."""
        try:
            obj = json.loads(self._extract_json(raw))
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(obj, dict):
            return None
        seg_data = obj.get("segments")
        if not isinstance(seg_data, list) or not seg_data:
            return None  # missing / not array / empty -> fail (spec §A.2)

        out: List[SegmentResult] = []
        for s in seg_data:
            if not isinstance(s, dict):
                return None
            text, code, stype = s.get("text"), s.get("code"), s.get("type")
            if not isinstance(text, str) or not text.strip():
                return None
            if not isinstance(code, str) or not isinstance(stype, str):
                return None
            code = code.strip().upper()
            stype = stype.strip().lower()
            if stype not in VALID_TYPES:
                return None
            if stype == "meta":
                if code != "META":
                    return None  # meta must use the META sentinel
                out.append(SegmentResult(text=text, segment_type="META",
                                         node_id="META", node_type="meta",
                                         category="meta"))
                continue
            # clinical content: code must map, and type must match the
            # mapped node's graph category bucket (spec §A.4).
            node_id = CODE_MAP.get(code)
            if node_id is None or node_id not in self.graph:
                return None
            graph_type = self.graph.nodes[node_id].get("type")
            if graph_type != stype:
                return None  # internal label/type inconsistency -> retry
            out.append(SegmentResult(
                text=text, segment_type="ACTION", node_id=node_id,
                node_type=graph_type,
                category=self.graph.nodes[node_id].get("category", "unknown"),
            ))
        return out

    # ---- post-hoc derivation (spec §A.5) -----------------------------

    def _derive(self, segments: List[SegmentResult], user_input: str) -> SafetyResult:
        # Step 1: mirror the structured META filter (critic.py:296)
        dream = [s for s in segments if s.node_type != "meta"]
        # Step 2: is_safe from non-META segments
        is_safe = not any(s.node_type == "maladaptive" for s in dream)
        # Step 3: primary node — highest-severity maladaptive, else first
        # dream segment, else META_ONLY (all-meta -> safe).
        maladaptive = [s for s in dream if s.node_type == "maladaptive"]
        if maladaptive:
            primary = min(maladaptive,
                          key=lambda s: SEVERITY_PRIORITY.get(s.node_id, 99))
            node_id, node_type = primary.node_id, "maladaptive"
            category = primary.category
        elif dream:
            p = dream[0]
            node_id, node_type, category = p.node_id, p.node_type, p.category
        else:
            node_id, node_type, category = "META_ONLY", "neutral", "meta"
            is_safe = True

        severity = None
        if not is_safe:
            sev_rank = SEVERITY_PRIORITY.get(node_id)
            severity = {1: "CRITICAL", 2: "HIGH", 3: "HIGH",
                        4: "MODERATE"}.get(sev_rank, "MODERATE")

        return SafetyResult(
            is_safe=is_safe, node_id=node_id, node_type=node_type,
            category=category, input_text=user_input,
            segments=segments, severity=severity,
        )

    # ---- public interface (matches SafetyCritic) ---------------------

    async def evaluate_intervention(self, user_input: str,
                                    nightmare_context: Optional[str] = None
                                    ) -> SafetyResult:
        if nightmare_context:
            llm_input = f'Context: "{nightmare_context}"\nInput: "{user_input}"'
        else:
            llm_input = f'Input: "{user_input}"'

        # Attempt 1
        try:
            resp, _, _ = await self.agent.generate(llm_input)
            segs = self._parse_and_validate(resp)
        except Exception as e:
            logger.warning(f"Stage-merge attempt 1 errored: {e}")
            segs = None

        # Attempt 2 (single retry with reminder, spec §A.4)
        if segs is None:
            try:
                resp, _, _ = await self.agent.generate(llm_input + _RETRY_REMINDER)
                segs = self._parse_and_validate(resp)
            except Exception as e:
                logger.warning(f"Stage-merge attempt 2 errored: {e}")
                segs = None

        if segs is None:
            logger.error("Stage-merge double parse failure -> PARSE_FAILURE")
            return SafetyResult(
                is_safe=False, node_id="PARSE_FAILURE",
                node_type="unclassified", category="unknown",
                input_text=user_input, segments=[],
                severity="CRITICAL", parse_failure=True,
            )

        return self._derive(segs, user_input)
