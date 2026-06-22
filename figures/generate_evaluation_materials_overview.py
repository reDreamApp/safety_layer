#!/usr/bin/env python3
"""Generate Figure 4.1: evaluation material and scoring status."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_BASE = ROOT / "figures" / "evaluation_materials_overview"


def load_cases(path: Path) -> list[dict]:
    suites = json.loads(path.read_text(encoding="utf-8"))
    cases = []
    for suite in suites:
        suite_name = suite.get("suite", "")
        for test in suite.get("tests", []):
            row = dict(test)
            row["suite"] = suite_name
            cases.append(row)
    return cases


def is_buried_alive(case: dict) -> bool:
    return "buried alive" in case.get("suite", "").lower()


def main() -> None:
    dev_cases = load_cases(ROOT / "data" / "benchmarks" / "dev_dataset.json")
    test_cases = load_cases(ROOT / "data" / "benchmarks" / "test_dataset.json")
    mal_mal_cases = load_cases(ROOT / "data" / "benchmarks" / "dev_dataset_mal_mal.json")

    dev_scored = sum(case.get("expected_safe") is not None for case in dev_cases)
    dev_boundary = sum(case.get("expected_safe") is None for case in dev_cases)

    test_excluded = sum(is_buried_alive(case) for case in test_cases)
    test_boundary = sum(
        (not is_buried_alive(case)) and case.get("expected_safe") is None
        for case in test_cases
    )
    test_primary = sum(
        (not is_buried_alive(case)) and case.get("expected_safe") is not None
        for case in test_cases
    )

    rows = [
        {
            "label": "Development benchmark",
            "segments": [
                ("Scored cases", dev_scored),
                ("Boundary / exploratory", dev_boundary),
            ],
        },
        {
            "label": "Held-out test set",
            "segments": [
                ("Primary test metrics", test_primary),
                ("Boundary / exploratory", test_boundary),
                ("Excluded truncated suite", test_excluded),
            ],
        },
        {
            "label": "Composite maladaptive slice",
            "segments": [
                ("Supplementary stress test", len(mal_mal_cases)),
            ],
        },
    ]

    colors = {
        "Scored cases": "#4C78A8",
        "Primary test metrics": "#4C78A8",
        "Boundary / exploratory": "#F2B447",
        "Excluded truncated suite": "#B8B8B8",
        "Supplementary stress test": "#59A14F",
    }

    fig, ax = plt.subplots(figsize=(7.2, 2.25))
    y_positions = list(range(len(rows)))[::-1]
    bar_height = 0.48

    for y, row in zip(y_positions, rows):
        left = 0
        for name, value in row["segments"]:
            ax.barh(
                y,
                value,
                left=left,
                height=bar_height,
                color=colors[name],
                edgecolor="white",
                linewidth=1,
            )
            if value >= 30:
                ax.text(
                    left + value / 2,
                    y,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=(
                        "white"
                        if name
                        in {
                            "Scored cases",
                            "Primary test metrics",
                            "Supplementary stress test",
                        }
                        else "#222222"
                    ),
                    fontweight="bold",
                )
            else:
                ax.text(
                    left + value + 5,
                    y,
                    str(value),
                    ha="left",
                    va="center",
                    fontsize=8.5,
                    color="#222222",
                    fontweight="bold",
                )
            left += value

    ax.set_yticks(y_positions)
    ax.set_yticklabels([row["label"] for row in rows], fontsize=10)
    ax.set_xlabel("Number of cases", fontsize=9)
    ax.set_xlim(0, 510)
    ax.grid(axis="x", color="#E5E5E5", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    fig.tight_layout()
    fig.savefig(f"{OUT_BASE}.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT_BASE}.png", dpi=220, bbox_inches="tight")
    print(f"Wrote {OUT_BASE}.pdf and {OUT_BASE}.png")


if __name__ == "__main__":
    main()
