"""
Ablation A — StageMergeCritic unit tests.

Spec: docs/planning/ablation_spec.md §"Ablation A" + Addendum 2.
Covers: valid parse + post-hoc derivation (§A.5), META filtering,
severity-priority primary selection, all-meta -> META_ONLY safe,
single-retry-then-success, fail-closed PARSE_FAILURE (§A.4), schema
validation (type/code consistency, meta sentinel, empty array), and
prompt-parity guards (§A.3: no severity/correction/CoT leakage).

Hermetic: safety.stage_merge_critic.Agent patched (no API key/network);
critic.agent.generate stubbed with canned LLM responses.
"""

import asyncio
import json
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from safety.stage_merge_critic import StageMergeCritic, STAGE_MERGE_PROMPT


def _critic(responses):
    """StageMergeCritic whose LLM returns the given list of strings in order."""
    with patch("safety.stage_merge_critic.Agent", MagicMock()):
        c = StageMergeCritic()
    c.agent.generate = AsyncMock(side_effect=[(r, {}, None) for r in responses])
    return c


def _run(c, text, ctx="ctx"):
    return asyncio.run(c.evaluate_intervention(text, nightmare_context=ctx))


# ---- valid parse + post-hoc derivation (§A.5) ------------------------

def test_valid_mixed_segments_derives_unsafe_and_filters_meta():
    payload = json.dumps({"segments": [
        {"text": "this exercise is dumb", "code": "META", "type": "meta"},
        {"text": "I hide under the bed", "code": "HIDE", "type": "maladaptive"},
        {"text": "then I call for help", "code": "HELP", "type": "adaptive"},
    ]})
    r = _run(_critic([payload]), "x")
    assert r.is_safe is False
    assert r.node_id == "AVOIDANCE"          # HIDE -> AVOIDANCE
    assert r.parse_failure is False
    # META labelled, not dropped from the segment list
    assert any(s.segment_type == "META" for s in r.segments)
    assert len(r.segments) == 3


def test_severity_priority_picks_most_critical_maladaptive():
    payload = json.dumps({"segments": [
        {"text": "I hide", "code": "HIDE", "type": "maladaptive"},          # AVOIDANCE prio 4
        {"text": "I butcher him", "code": "DESTROY", "type": "maladaptive"}, # VIOLENT_REVENGE prio 1
    ]})
    r = _run(_critic([payload]), "x")
    assert r.is_safe is False
    assert r.node_id == "VIOLENT_REVENGE"     # highest severity wins
    assert r.severity == "CRITICAL"


def test_all_meta_is_safe_meta_only():
    payload = json.dumps({"segments": [
        {"text": "I hate this therapy", "code": "META", "type": "meta"},
    ]})
    r = _run(_critic([payload]), "x")
    assert r.is_safe is True
    assert r.node_id == "META_ONLY"


def test_all_adaptive_is_safe():
    payload = json.dumps({"segments": [
        {"text": "I fight back", "code": "CONFRONT", "type": "adaptive"},
    ]})
    r = _run(_critic([payload]), "x")
    assert r.is_safe is True
    assert r.node_id == "BEHAVIORAL_MASTERY"


# ---- retry / fail-closed (§A.4) --------------------------------------

def test_single_retry_then_success():
    bad = "sorry, here is the analysis: the user hides."
    good = json.dumps({"segments": [{"text": "I hide", "code": "HIDE", "type": "maladaptive"}]})
    c = _critic([bad, good])
    r = _run(c, "x")
    assert c.agent.generate.await_count == 2
    assert r.parse_failure is False and r.node_id == "AVOIDANCE"


def test_double_failure_is_parse_failure():
    c = _critic(["not json", "still not json"])
    r = _run(c, "x")
    assert c.agent.generate.await_count == 2
    assert r.parse_failure is True
    assert r.node_id == "PARSE_FAILURE" and r.is_safe is False
    assert r.segments == []


def test_type_code_inconsistency_triggers_retry_then_fails():
    # HIDE is maladaptive; declaring it adaptive is internal inconsistency
    bad = json.dumps({"segments": [{"text": "I hide", "code": "HIDE", "type": "adaptive"}]})
    c = _critic([bad, bad])
    r = _run(c, "x")
    assert c.agent.generate.await_count == 2
    assert r.parse_failure is True


def test_meta_without_sentinel_is_invalid():
    bad = json.dumps({"segments": [{"text": "hi", "code": "HIDE", "type": "meta"}]})
    c = _critic([bad, bad])
    assert _run(c, "x").parse_failure is True


def test_empty_segments_array_is_invalid():
    c = _critic([json.dumps({"segments": []}), json.dumps({"segments": []})])
    assert _run(c, "x").parse_failure is True


def test_markdown_fenced_json_is_recovered():
    payload = "```json\n" + json.dumps(
        {"segments": [{"text": "I wake myself up", "code": "ESCAPE", "type": "maladaptive"}]}
    ) + "\n```"
    r = _run(_critic([payload]), "x")
    assert r.parse_failure is False and r.node_id == "INTERRUPTION"


# ---- prompt parity guards (§A.3 / §"Don'ts") -------------------------

def test_prompt_has_clinical_body_and_schema():
    assert "Clinical Coder for Imagery Rehearsal Therapy" in STAGE_MERGE_PROMPT
    assert "Violence Threshold" in STAGE_MERGE_PROMPT          # rules retained
    assert '"segments"' in STAGE_MERGE_PROMPT                  # JSON schema
    assert "META" in STAGE_MERGE_PROMPT


def test_prompt_excludes_severity_correction_and_cot():
    low = STAGE_MERGE_PROMPT.lower()
    assert "severity_priority" not in low
    assert "correction" not in low and "redirect" not in low
    assert "step by step" not in low and "think through" not in low  # no CoT


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
