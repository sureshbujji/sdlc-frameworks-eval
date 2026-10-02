"""Spec registry integrity: 8 requirements, unique IDs, valid AC refs."""

from sdlc_eval import spec as S


def test_eight_requirements():
    assert len(S.REQUIREMENTS) == 8
    assert S.REQUIREMENT_IDS == tuple(f"R{i}" for i in range(1, 9))


def test_acceptance_criteria_ids_reference_parent():
    for req in S.REQUIREMENTS:
        assert len(req.criteria) >= 2
        for i, ac in enumerate(req.criteria, start=1):
            assert ac.id == f"{req.id}-AC{i}"


def test_total_criteria_count():
    assert S.TOTAL_CRITERIA == sum(len(r.criteria) for r in S.REQUIREMENTS)
    assert S.TOTAL_CRITERIA > 0


def test_priorities_valid():
    for req in S.REQUIREMENTS:
        assert req.priority in ("must", "should")
