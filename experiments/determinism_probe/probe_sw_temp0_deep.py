"""
Targeted deep probe: SW_temp0 only, N=20 per case on the 6 regression inputs.

Goal: yesterday's probe showed SW_temp0 = 0/6 drift. Today's probe (2026-04-23)
showed SW_temp0 = 1/6 drift ("Same locked room": 3x ACTION|ACTION, 2x THOUGHT|ACTION).
This script increases N to 20 to characterize whether "Same locked room" is
a rare-flip borderline case (e.g. 1-in-10) or flips roughly 50/50, and whether
any other case we thought was stable also drifts at higher N.
"""

from __future__ import annotations

import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from AI.agent import Agent, MODELS
from safety.critic import SEGMENTER_PROMPT


REGRESSION_KEYS = [
    ("Fighting a regenerating demon",          "Realize I am safe"),
    ("Trapped in a room full of snakes",       "Same locked room"),
    ("Lost in a foreign city",                 "Lift above the city"),
    ("Failing a test in front of a mocking",   "Refuse public shaming"),
    ("Looking in a mirror and seeing",         "Relief in the mirror"),
    ("Trying to run through thick mud",        "turn and pull free"),
]

N_REPEATS = 20


def load_cases():
    dev = json.loads((ROOT / "data/benchmarks/dev_dataset.json").read_text())
    out = []
    for suite_prefix, desc in REGRESSION_KEYS:
        for suite in dev:
            if suite_prefix in suite.get("suite", ""):
                for t in suite.get("tests", []):
                    if desc in t.get("description", ""):
                        out.append({
                            "description": desc,
                            "suite": suite["suite"],
                            "nightmare": suite.get("nightmare_context", ""),
                            "input": t["input"],
                        })
                        break
    return out


def signature(segments):
    return "|".join(seg.get("type", "?") for seg in segments) if segments else "(empty)"


async def segment_once(agent, nightmare, user_input):
    prompt = f'Context: "{nightmare}"\nInput: "{user_input}"'
    response, _, _ = await agent.generate(prompt)
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return []


async def main():
    cases = load_cases()
    print(f"Loaded {len(cases)} cases. Running N={N_REPEATS} calls each on SW+temp=0.")
    print()

    agent = Agent(
        model_config=MODELS["MISTRAL_NEMO"],
        system_prompt=SEGMENTER_PROMPT,
        temperature=0,
    )

    results = []
    for case in cases:
        sigs = []
        for _ in range(N_REPEATS):
            segs = await segment_once(agent, case["nightmare"], case["input"])
            sigs.append(signature(segs))
        counter = Counter(sigs)
        n_unique = len(counter)
        results.append({
            "description": case["description"],
            "n_unique": n_unique,
            "most_common": counter.most_common(),
        })
        print(f"  {case['description']:35s} unique={n_unique}/{N_REPEATS}  counts={dict(counter)}")

    print()
    drift_cases = sum(1 for r in results if r["n_unique"] > 1)
    print(f"Summary: {drift_cases}/{len(results)} cases drifted over N={N_REPEATS}.")

    out_path = ROOT / "data/benchmarks/segmenter_sw_temp0_deep_probe.json"
    out_path.write_text(json.dumps({"n_repeats": N_REPEATS, "results": results}, indent=2))
    print(f"JSON → {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
