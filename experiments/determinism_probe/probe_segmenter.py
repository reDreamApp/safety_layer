"""
Segmenter determinism probe.

Purpose:
    The full-set semantic-consistency benchmark (2026-04-22) surfaced 6 S1
    regressions where the classifier's answer flipped between the N=1 baseline
    run and the N=5 consistency run on the SAME input. Per-case inspection
    traced every regression to the segmenter producing a different segment
    structure across runs — NOT vote aggregation. This probe measures that
    drift directly: we call the segmenter N=5 times on each of the 6 regression
    inputs under a 2x2 design (provider x temperature):

        [1] OpenRouter (current) × temperature=0.1  (reproduces observed config)
        [2] OpenRouter (current) × temperature=0
        [3] Scaleway (direct)    × temperature=0.1
        [4] Scaleway (direct)    × temperature=0

    If the drift is driven primarily by temperature, [2] and [4] should be
    stable. If it is driven primarily by OpenRouter aggregator non-determinism,
    [3] and [4] should be stable. The 2x2 disentangles these.

Output:
    A JSON report + a human-readable summary. See run_probe() for structure.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

# Project root on path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from AI.agent import Agent, MODELS
from safety.critic import SEGMENTER_PROMPT


# -----------------------------------------------------------------------------
# The 6 S1 regression cases (identified from benchmark_results_s1_consistency.csv)
# -----------------------------------------------------------------------------
# We pull the canonical (suite_prefix, test_description) pairs. At runtime we
# match these against data/benchmarks/dev_dataset.json to recover the full
# nightmare context + user input.
REGRESSION_KEYS = [
    ("Fighting a regenerating demon",          "Realize I am safe"),
    ("Trapped in a room full of snakes",       "Same locked room"),
    ("Lost in a foreign city",                  "Lift above the city"),
    ("Failing a test in front of a mocking",   "Refuse public shaming"),
    ("Looking in a mirror and seeing",         "Relief in the mirror"),
    ("Trying to run through thick mud",        "turn and pull free"),
]

N_REPEATS = 5
DATASET_PATH = ROOT / "data" / "benchmarks" / "dev_dataset.json"
REPORT_PATH = ROOT / "data" / "benchmarks" / "segmenter_determinism_probe.json"
SUMMARY_PATH = ROOT / "data" / "benchmarks" / "segmenter_determinism_probe.md"


@dataclass
class Condition:
    name: str
    model_key: str
    temperature: float


CONDITIONS: List[Condition] = [
    Condition("OR_temp0.1", "OR_MISTRAL_NEMO", 0.1),  # current production
    Condition("OR_temp0",   "OR_MISTRAL_NEMO", 0.0),
    Condition("SW_temp0.1", "MISTRAL_NEMO",    0.1),
    Condition("SW_temp0",   "MISTRAL_NEMO",    0.0),
]


def load_regression_cases() -> List[dict]:
    """Resolve REGRESSION_KEYS against dev_dataset.json → {suite, nightmare, desc, input}."""
    with DATASET_PATH.open() as f:
        dataset = json.load(f)

    cases = []
    for suite_prefix, desc in REGRESSION_KEYS:
        match = None
        for suite in dataset:
            if suite["suite"].startswith(suite_prefix):
                for t in suite.get("tests", []):
                    if t.get("description") == desc:
                        match = {
                            "suite": suite["suite"],
                            "nightmare": suite["nightmare"],
                            "description": desc,
                            "input": t["input"],
                        }
                        break
            if match:
                break
        if not match:
            raise RuntimeError(f"Could not resolve regression case: {suite_prefix!r} / {desc!r}")
        cases.append(match)
    return cases


async def call_segmenter_once(agent: Agent, user_input: str, nightmare: str) -> dict:
    """Single segmenter call. Returns structured result or parse-error info."""
    prompt = f"Context: \"{nightmare}\"\nInput: \"{user_input}\""
    try:
        response, _, _ = await agent.generate(prompt)
    except Exception as e:
        return {"error": f"api_error: {type(e).__name__}: {e}", "raw": None, "segments": None}

    raw = response
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    si, ei = cleaned.find("["), cleaned.rfind("]")
    if si != -1 and ei != -1 and ei > si:
        cleaned = cleaned[si : ei + 1]
    try:
        parsed = json.loads(cleaned)
        segments = [
            {"text": s.get("text", ""), "type": s.get("type", "?").upper(), "context": s.get("context")}
            for s in parsed
        ]
        return {"error": None, "raw": raw, "segments": segments}
    except json.JSONDecodeError as e:
        return {"error": f"parse_error: {e}", "raw": raw, "segments": None}


def signature(segments) -> str:
    """Compact signature of segment structure: "TYPE|TYPE|TYPE" on segment-type sequence only."""
    if segments is None:
        return "<PARSE_ERROR>"
    return "|".join(s["type"] for s in segments)


def detailed_signature(segments) -> str:
    """Longer signature including the first ~30 chars of each segment's text."""
    if segments is None:
        return "<PARSE_ERROR>"
    return " || ".join(f"[{s['type']}] {s['text'][:40]}" for s in segments)


async def run_one_condition(cond: Condition, cases: List[dict]) -> dict:
    """Run the segmenter N_REPEATS times per case under one (provider, temp) condition."""
    agent = Agent(
        model_config=MODELS[cond.model_key],
        system_prompt=SEGMENTER_PROMPT,
        temperature=cond.temperature,
    )
    results = []
    for case in cases:
        runs = []
        for _ in range(N_REPEATS):
            r = await call_segmenter_once(agent, case["input"], case["nightmare"])
            runs.append(r)
        sigs = [signature(r["segments"]) for r in runs]
        n_unique = len(set(sigs))
        results.append(
            {
                "description": case["description"],
                "n_unique_signatures": n_unique,
                "signatures": sigs,
                "detailed_signatures": [detailed_signature(r["segments"]) for r in runs],
                "errors": [r["error"] for r in runs],
            }
        )
    return {"condition": cond.name, "model_key": cond.model_key, "temperature": cond.temperature, "cases": results}


async def main() -> None:
    cases = load_regression_cases()
    print(f"Loaded {len(cases)} regression cases.")
    print(f"Running {len(CONDITIONS)} conditions x {len(cases)} cases x N={N_REPEATS} repeats = "
          f"{len(CONDITIONS) * len(cases) * N_REPEATS} segmenter calls.\n")

    all_results = []
    for cond in CONDITIONS:
        print(f"[condition] {cond.name}  (model={cond.model_key}, temp={cond.temperature})")
        res = await run_one_condition(cond, cases)
        all_results.append(res)
        for case in res["cases"]:
            print(f"   {case['description'][:40]:40s}  unique={case['n_unique_signatures']}/{N_REPEATS}  "
                  f"sigs={case['signatures']}")
        print()

    REPORT_PATH.write_text(json.dumps({"cases": [{"description": c["description"],
                                                  "suite": c["suite"],
                                                  "input": c["input"]} for c in cases],
                                       "conditions": all_results,
                                       "n_repeats": N_REPEATS}, indent=2))
    print(f"JSON report → {REPORT_PATH}")

    # Markdown summary
    lines = ["# Segmenter determinism probe", ""]
    lines.append(f"N={N_REPEATS} segmenter calls per case in each of 4 conditions.\n")
    lines.append("## Aggregate: mean unique signatures across 6 cases (lower = more stable)\n")
    lines.append("| Condition | Mean unique sigs / 5 | Cases with drift |")
    lines.append("|---|---|---|")
    for res in all_results:
        uniqs = [c["n_unique_signatures"] for c in res["cases"]]
        drifted = sum(1 for u in uniqs if u > 1)
        lines.append(f"| {res['condition']} | {sum(uniqs)/len(uniqs):.2f} | {drifted}/6 |")
    lines.append("")
    for res in all_results:
        lines.append(f"## Condition: {res['condition']} (model={res['model_key']}, temp={res['temperature']})\n")
        for case in res["cases"]:
            lines.append(f"### {case['description']}")
            lines.append(f"Unique type-sequence signatures across 5 runs: **{case['n_unique_signatures']}**")
            lines.append("")
            for i, (sig, det) in enumerate(zip(case["signatures"], case["detailed_signatures"])):
                lines.append(f"- run {i+1}: `{sig}` — {det}")
            lines.append("")
    SUMMARY_PATH.write_text("\n".join(lines))
    print(f"Summary → {SUMMARY_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
