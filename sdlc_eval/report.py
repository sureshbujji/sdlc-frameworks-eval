"""Markdown + JSON report rendering."""

import json
from datetime import date

from . import spec as S
from .frameworks import FRAMEWORK_BLURBS


def render_table(ranked):
    header = ("| Framework | Fidelity | Coverage | Traceability | AC alignment "
              "| Tests/req | Docs |")
    sep = "|---|---|---|---|---|---|---|"
    rows = []
    for s in ranked:
        name = FRAMEWORK_BLURBS[s.framework].split(" — ")[0]
        rows.append(
            f"| {name} | {s.fidelity_score:.1f} | {s.requirement_coverage:.0%} "
            f"| {s.traceability:.0%} | {s.ac_alignment:.0%} "
            f"| {s.test_density:.2f} | {s.doc_completeness:.0%} |"
        )
    return "\n".join([header, sep] + rows)


def render_report(ranked, artifacts):
    lines = [
        f"# SDLC Frameworks Eval — {S.FEATURE_NAME} ({date.today().isoformat()})",
        "",
        f"Feature: {S.FEATURE_BLURB}",
        f"Requirements: {len(S.REQUIREMENTS)} "
        f"({S.TOTAL_CRITERIA} acceptance criteria)",
        "",
        "## Fidelity ranking",
        "",
        render_table(ranked),
        "",
        "## Pipeline notes",
        "",
    ]
    for a in artifacts:
        lines.append(f"- **{FRAMEWORK_BLURBS[a.framework]}**: {a.pipeline_notes}")
    lines += [
        "",
        "## Reading the results",
        "",
        "- **Coverage**: share of R1–R8 with a real implementation in generated code.",
        "- **Traceability**: requirements cited in both code and tests.",
        "- **AC alignment**: acceptance criteria quoted verbatim in tests.",
        "- Methodology simulations are deterministic; no LLM calls are made.",
    ]
    return "\n".join(lines) + "\n"


def to_json(ranked):
    return json.dumps(
        [
            {
                "framework": s.framework,
                "fidelity_score": s.fidelity_score,
                "requirement_coverage": s.requirement_coverage,
                "traceability": s.traceability,
                "ac_alignment": s.ac_alignment,
                "test_density": s.test_density,
                "doc_completeness": s.doc_completeness,
            }
            for s in ranked
        ],
        indent=2,
    )
