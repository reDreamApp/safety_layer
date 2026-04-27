"""Produce integration_eval_summary.md from the judged CSV.

Reads integration_eval_results.csv (two rows per scenario, each with judge
columns) and writes:
  - A/B headline table (control vs treatment, Δ)
  - Per-node A/B breakdown
  - Three paired examples illustrating (a) safety-layer-helped,
    (b) safety-layer-didn't-help, (c) control-already-fine
  - Off-label section for cases where detected_node != expected_node

Usage:
    uv run python experiments/integration_eval/summarize_results.py \
        --input data/integration_eval/integration_eval_results.csv \
        --output data/integration_eval/integration_eval_summary.md
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

QUALITY_LEVELS = ["strong", "partial", "absent"]


def pct(n: int, d: int) -> str:
    if d == 0:
        return "—"
    return f"{100.0 * n / d:.1f}%"


def aggregate(rows):
    """Group rows into scenarios, return dict keyed by condition with counts."""
    counts = {cond: {k: 0 for k in QUALITY_LEVELS + ["echoes", "total"]} for cond in ("control", "treatment")}
    for r in rows:
        cond = r["condition"]
        counts[cond]["total"] += 1
        q = (r.get("judge_redirect_quality") or "").strip()
        if q in QUALITY_LEVELS:
            counts[cond][q] += 1
        echoes = (r.get("judge_echoes_maladaptive") or "").strip().lower()
        if echoes in ("true", "1", "yes"):
            counts[cond]["echoes"] += 1
    return counts


def render_headline(counts) -> str:
    lines = [
        "| Condition | strong | partial | absent | echoes maladaptive |",
        "|---|---|---|---|---|",
    ]
    for cond_label, cond_key in [("Control (no safety)", "control"), ("Treatment (with safety)", "treatment")]:
        c = counts[cond_key]
        tot = c["total"]
        lines.append(
            f"| {cond_label} | {pct(c['strong'], tot)} | {pct(c['partial'], tot)} | "
            f"{pct(c['absent'], tot)} | {pct(c['echoes'], tot)} |"
        )
    # Delta row
    ctl, trt = counts["control"], counts["treatment"]
    def delta(metric):
        if ctl["total"] == 0 or trt["total"] == 0:
            return "—"
        d = (100.0 * trt[metric] / trt["total"]) - (100.0 * ctl[metric] / ctl["total"])
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.1f} pp"
    lines.append(
        f"| **Δ (safety layer lift)** | {delta('strong')} | {delta('partial')} | "
        f"{delta('absent')} | {delta('echoes')} |"
    )
    return "\n".join(lines)


def render_per_node(rows) -> str:
    by_node = defaultdict(list)
    for r in rows:
        by_node[r["expected_node"]].append(r)

    lines = ["| Node | Cond | strong | partial | absent | echoes | N |", "|---|---|---|---|---|---|---|"]
    for node in ["AVOIDANCE", "INTERRUPTION", "VIOLENT_REVENGE", "SUPPRESSION", "TRAUMA_REPLAY"]:
        node_rows = by_node.get(node, [])
        counts = aggregate(node_rows)
        for cond_label, cond_key in [("ctrl", "control"), ("trt", "treatment")]:
            c = counts[cond_key]
            tot = c["total"]
            lines.append(
                f"| {node} | {cond_label} | {pct(c['strong'], tot)} | {pct(c['partial'], tot)} | "
                f"{pct(c['absent'], tot)} | {pct(c['echoes'], tot)} | {tot} |"
            )
    return "\n".join(lines)


def pick_paired_examples(rows):
    """Return three (case_id, reason, control_row, treatment_row) tuples."""
    scenarios = defaultdict(dict)
    for r in rows:
        scenarios[r["case_id"]][r["condition"]] = r
    paired = [
        (cid, pair) for cid, pair in scenarios.items()
        if "control" in pair and "treatment" in pair
    ]

    q_rank = {"absent": 0, "partial": 1, "strong": 2, "": -1}

    safety_helped = []       # ctrl weak, trt strong
    safety_didnt_help = []   # trt still absent
    ctrl_already_fine = []   # ctrl strong and trt strong (safety added nothing)
    for cid, pair in paired:
        ctl_q = (pair["control"].get("judge_redirect_quality") or "").strip()
        trt_q = (pair["treatment"].get("judge_redirect_quality") or "").strip()
        ctl_rank = q_rank.get(ctl_q, -1)
        trt_rank = q_rank.get(trt_q, -1)
        if trt_rank > ctl_rank and trt_q == "strong":
            safety_helped.append((cid, pair))
        if trt_q == "absent":
            safety_didnt_help.append((cid, pair))
        if ctl_q == "strong" and trt_q == "strong":
            ctrl_already_fine.append((cid, pair))

    # Pick one of each if available
    picks = []
    if safety_helped:
        picks.append(("Safety layer corrected a weak control", safety_helped[0]))
    if safety_didnt_help:
        picks.append(("Treatment still failed despite the constraint", safety_didnt_help[0]))
    if ctrl_already_fine:
        picks.append(("Control was already adequate; safety added little", ctrl_already_fine[0]))
    return picks


def render_paired_examples(picks) -> str:
    if not picks:
        return "_No paired examples to display._"
    chunks = []
    for reason, (cid, pair) in picks:
        ctl = pair["control"]
        trt = pair["treatment"]
        chunks.append(
            f"### {cid} — {reason}\n\n"
            f"**Expected node:** {ctl['expected_node']}  |  **Detected:** {ctl['detected_node']}  "
            f"|  **Severity:** {ctl.get('severity', '—')}\n\n"
            f"**User's maladaptive attempt:**\n> {ctl['user_input']}\n\n"
            f"**Control response** (redirect_quality=`{ctl.get('judge_redirect_quality', '')}`, "
            f"echoes=`{ctl.get('judge_echoes_maladaptive', '')}`):\n> {ctl['response']}\n\n"
            f"**Treatment response** (redirect_quality=`{trt.get('judge_redirect_quality', '')}`, "
            f"echoes=`{trt.get('judge_echoes_maladaptive', '')}`):\n> {trt['response']}\n\n"
            f"**Judge reasoning (control):** {ctl.get('judge_reasoning', '')}\n\n"
            f"**Judge reasoning (treatment):** {trt.get('judge_reasoning', '')}\n"
        )
    return "\n---\n\n".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/integration_eval/integration_eval_results.csv")
    parser.add_argument("--output", default="data/integration_eval/integration_eval_summary.md")
    args = parser.parse_args()

    input_path = REPO_ROOT / args.input
    output_path = REPO_ROOT / args.output

    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    all_case_ids = sorted({r["case_id"] for r in rows})
    unsafe_rows = [r for r in rows if (r.get("critic_classified_unsafe") or "").lower() == "true"]
    excluded_case_ids = sorted({
        r["case_id"] for r in rows
        if (r.get("critic_classified_unsafe") or "").lower() != "true"
    })
    off_label_case_ids = sorted({
        r["case_id"] for r in rows
        if (r.get("node_match") or "").lower() == "false"
        and (r.get("critic_classified_unsafe") or "").lower() == "true"
    })

    main_rows = [r for r in unsafe_rows if (r.get("tier") or "main") == "main"]
    multipart_rows = [r for r in unsafe_rows if (r.get("tier") or "main") == "multipart"]

    md = []
    md.append("# Integration Eval Summary — Constraint-Redirect Validation\n")
    md.append(f"**Scenarios in set:** {len(all_case_ids)}  ")
    md.append(f"**Critic classified unsafe (included in headline):** {len({r['case_id'] for r in unsafe_rows})}  ")
    md.append(f"**Excluded (critic said safe):** {len(excluded_case_ids)}  ")
    md.append(f"**Off-label (detected ≠ expected):** {len(off_label_case_ids)}  \n")

    # Main tier — pure maladaptive (tests Correct)
    md.append("## Main tier — A/B Headline (pure maladaptive inputs, tests Correct)\n")
    md.append(render_headline(aggregate(main_rows)) + "\n")
    md.append("### Per-Node Breakdown (main tier)\n")
    md.append(render_per_node(main_rows) + "\n")
    md.append("### Paired Examples (main tier)\n")
    md.append(render_paired_examples(pick_paired_examples(main_rows)) + "\n")

    # Supplementary tier — adaptive+maladaptive multipart (tests Validate+Correct)
    if multipart_rows:
        md.append("## Multipart tier — A/B Headline (adaptive + maladaptive inputs, tests Validate+Correct)\n")
        md.append(
            "_Smaller supplementary set (8 scenarios). Coverage is 0 for SUPPRESSION and "
            "TRAUMA_REPLAY in the dev dataset's multipart slice — flagged as a dataset-gen gap._\n"
        )
        md.append(render_headline(aggregate(multipart_rows)) + "\n")
        md.append("### Per-Node Breakdown (multipart tier)\n")
        md.append(render_per_node(multipart_rows) + "\n")
        md.append("### Paired Examples (multipart tier)\n")
        md.append(render_paired_examples(pick_paired_examples(multipart_rows)) + "\n")
    if excluded_case_ids:
        md.append("## Excluded cases (critic classified as SAFE)\n")
        md.append(", ".join(excluded_case_ids) + "\n")
    if off_label_case_ids:
        md.append("## Off-label cases (detected_node ≠ expected_node)\n")
        md.append(
            "These cases are kept in the CSV for transparency but their headline Δ "
            "reflects classifier disagreement rather than constraint-handling failure.\n\n"
        )
        md.append(", ".join(off_label_case_ids) + "\n")
    md.append("\n---\n")
    md.append(
        "_Ramon's manual calibration pass (~5 judge ratings spot-checked by hand) "
        "is not automated; do this before citing numbers in the thesis._\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md))
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
