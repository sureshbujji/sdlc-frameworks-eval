"""Spec-to-code fidelity scorer.

Dimensions (all derived by static analysis of the generated artifacts):
- requirement_coverage: share of R1..R8 cited (REQ-<id>) in generated code.
  A requirement counts as covered only if its citation is attached to a
  real implementation (a `def` block), not a DEFERRED/PARTIAL marker alone.
  PARTIAL (MetaGPT R8) still counts -- it shipped, just incompletely.
- traceability: share of requirements cited in BOTH code and tests.
- ac_alignment: share of acceptance-criterion texts quoted in the tests.
- test_density: number of `def test_` functions per requirement.
- doc_completeness: share of expected doc sections present.
- fidelity_score: weighted composite 0..100.

Weights: coverage 35, traceability 25, ac_alignment 20,
         normalized test density 10, doc completeness 10.
"""

import re

from . import spec as S
from .artifacts import FidelityScores, FrameworkArtifacts

REQ_RE = re.compile(r"REQ-(R\d+)")
TEST_RE = re.compile(r"^def (test_\w+)", re.MULTILINE)
DEF_RE = re.compile(r"^def (\w+)", re.MULTILINE)

EXPECTED_DOC_SECTIONS = {
    "metagpt": ["PRD", "System design", "QA report"],
    "speckit": ["constitution", "spec.md", "plan.md", "tasks.md"],
    "bmad": ["epic-1", "stories"],
}


def _cited_requirements(text):
    return set(REQ_RE.findall(text))


def _implemented_requirements(code):
    """Requirements whose citation sits inside a real `def` block
    (excludes bare DEFERRED comments with no implementation)."""
    implemented = set()
    current_defs = []  # stack of (def_name, cited_reqs)
    for line in code.splitlines():
        m = DEF_RE.match(line)
        if m and not line.startswith(" ") and not line.startswith("\t"):
            current_defs.append(set())
        for req in REQ_RE.findall(line):
            if current_defs and "DEFERRED" not in line:
                current_defs[-1].add(req)
    # flatten: union of all def-level citations
    for s in current_defs:
        implemented |= s
    # PARTIAL still counts as implemented (it shipped code).
    for line in code.splitlines():
        if "PARTIAL" in line:
            implemented |= set(REQ_RE.findall(line))
    return implemented & set(S.REQUIREMENT_IDS)


def score(artifacts: FrameworkArtifacts) -> FidelityScores:
    fw = artifacts.framework
    code_reqs = _implemented_requirements(artifacts.code)
    test_reqs = _cited_requirements(artifacts.tests) & set(S.REQUIREMENT_IDS)

    n = len(S.REQUIREMENTS)
    coverage = len(code_reqs) / n
    traceability = len(code_reqs & test_reqs) / n

    total_ac = S.TOTAL_CRITERIA
    ac_hits = sum(
        1 for r in S.REQUIREMENTS for ac in r.criteria
        if ac.text in artifacts.tests
    )
    ac_alignment = ac_hits / total_ac

    n_tests = len(TEST_RE.findall(artifacts.tests))
    density = n_tests / n
    density_norm = min(density / 3.0, 1.0)  # 3 tests/req saturates

    sections = EXPECTED_DOC_SECTIONS[fw]
    doc_hits = sum(1 for s in sections if s.lower() in artifacts.docs.lower())
    doc_completeness = doc_hits / len(sections)

    fidelity = round(
        35 * coverage + 25 * traceability + 20 * ac_alignment
        + 10 * density_norm + 10 * doc_completeness, 2,
    )
    return FidelityScores(
        framework=fw,
        requirement_coverage=round(coverage, 4),
        traceability=round(traceability, 4),
        ac_alignment=round(ac_alignment, 4),
        test_density=round(density, 3),
        test_density_norm=round(density_norm, 4),
        doc_completeness=round(doc_completeness, 4),
        fidelity_score=fidelity,
    )


def rank(scores):
    return sorted(scores, key=lambda s: s.fidelity_score, reverse=True)
