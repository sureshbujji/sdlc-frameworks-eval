"""Generator properties: methodology traits are actually present."""

from sdlc_eval import frameworks
from sdlc_eval import spec as S


def _all():
    return {name: gen() for name, gen in frameworks.GENERATORS.items()}


def test_all_three_frameworks_generate():
    arts = _all()
    assert set(arts) == {"metagpt", "speckit", "bmad"}
    for a in arts.values():
        assert a.code.strip() and a.tests.strip() and a.docs.strip()
        assert a.pipeline_notes


def test_generators_are_deterministic():
    first = _all()
    second = _all()
    for name in first:
        assert first[name].code == second[name].code
        assert first[name].tests == second[name].tests
        assert first[name].docs == second[name].docs


def test_speckit_cites_every_requirement_in_code():
    code = _all()["speckit"].code
    for req in S.REQUIREMENTS:
        assert f"REQ-{req.id}" in code


def test_bmad_defers_r7():
    bmad = _all()["bmad"]
    assert "DEFERRED" in bmad.code
    # R7 has no implementation: citation must not sit inside a def block
    assert "def record_metrics" not in bmad.code


def test_metagpt_flags_r8_partial():
    code = _all()["metagpt"].code
    assert "PARTIAL" in code
    assert "def graceful_shutdown" in code


def test_metagpt_qa_adds_regression_tests():
    tests = _all()["metagpt"].tests
    n_must = sum(1 for r in S.REQUIREMENTS if r.priority == "must")
    assert tests.count("qa_regression") == n_must


def test_generated_code_parses_as_python():
    import ast
    for a in _all().values():
        ast.parse(a.code)
        ast.parse(a.tests)
