"""Scorer correctness on real and synthetic artifacts."""

from sdlc_eval import frameworks, report
from sdlc_eval import spec as S
from sdlc_eval.artifacts import FrameworkArtifacts
from sdlc_eval.scorer import rank, score


def _scores():
    arts = [gen() for gen in frameworks.GENERATORS.values()]
    return {a.framework: score(a) for a in arts}


def test_scores_bounded():
    for s in _scores().values():
        assert 0 <= s.fidelity_score <= 100
        for f in ("requirement_coverage", "traceability", "ac_alignment",
                  "doc_completeness"):
            assert 0 <= getattr(s, f) <= 1


def test_speckit_full_coverage():
    s = _scores()["speckit"]
    assert s.requirement_coverage == 1.0
    assert s.traceability == 1.0


def test_bmad_misses_r7_coverage():
    s = _scores()["bmad"]
    assert s.requirement_coverage == 7 / 8
    assert s.traceability == 7 / 8


def test_metagpt_full_coverage_partial_r8():
    s = _scores()["metagpt"]
    assert s.requirement_coverage == 1.0  # PARTIAL still shipped


def test_ac_alignment_bmad_and_speckit_high():
    scores = _scores()
    # every non-deferred AC is quoted in tests for bmad/speckit
    for fw in ("bmad", "speckit"):
        assert scores[fw].ac_alignment >= 0.8


def test_perfect_artifact_scores_100():
    code, tests = [], []
    for req in S.REQUIREMENTS:
        code.append(f"def fn_{req.id.lower()}():\n    # REQ-{req.id}\n    pass\n")
        # 3 tests per requirement saturates the normalized test-density term
        for k in range(3):
            tests.append(f"def test_{req.id.lower()}_{k}():\n")
            for ac in req.criteria:
                tests.append(f"    # REQ-{req.id} | {ac.id}: {ac.text}\n    assert True\n")
    docs = "PRD\nSystem design\nQA report\nconstitution\nspec.md\nplan.md\ntasks.md\nepic-1\nstories\n"
    art = FrameworkArtifacts("speckit", "\n".join(code), "\n".join(tests), docs)
    s = score(art)
    assert s.requirement_coverage == 1.0
    assert s.traceability == 1.0
    assert s.ac_alignment == 1.0
    assert s.fidelity_score == 100.0


def test_empty_artifact_scores_zero():
    art = FrameworkArtifacts("bmad", "", "", "")
    s = score(art)
    assert s.fidelity_score == 0.0


def test_rank_is_sorted_descending():
    ranked = rank(list(_scores().values()))
    vals = [s.fidelity_score for s in ranked]
    assert vals == sorted(vals, reverse=True)
    assert {s.framework for s in ranked} == {"metagpt", "speckit", "bmad"}


def test_report_renders_table_and_json():
    arts = [gen() for gen in frameworks.GENERATORS.values()]
    ranked = rank([score(a) for a in arts])
    table = report.render_table(ranked)
    assert "Fidelity" in table and table.count("|") > 10
    import json
    data = json.loads(report.to_json(ranked))
    assert len(data) == 3 and all("fidelity_score" in d for d in data)
