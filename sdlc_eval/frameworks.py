"""Methodology-driven artifact generators for the three SDLC frameworks.

IMPORTANT: these are *simulations* of each framework's published methodology,
not live runs of the frameworks themselves (which require LLM backends).
Each generator encodes the framework's characteristic pipeline stages and
its documented failure modes, so the benchmark measures *methodology*
differences in spec-to-code fidelity on a fixed spec:

- MetaGPT: SOP multi-agent pipeline (PM -> Architect -> Engineer -> QA).
  QA agent re-verifies every requirement -> high test density. Documented
  failure mode: nuance is lost in the Architect->Engineer handoff for edge
  requirements, so R8 (graceful shutdown) ships partially (no drain timeout).
- Spec Kit (GitHub spec-kit): constitution -> specify -> plan -> tasks ->
  implement. Plan-first discipline -> strict traceability (every function
  cites requirement IDs) and a task checklist covering all 8 requirements,
  but thinner tests (one per acceptance criterion).
- BMAD (agile method): sharded PRD/architecture docs, dev stories per epic.
  Acceptance criteria are copied verbatim into tests -> strongest AC
  alignment, but R7 (observability) is deferred to "Epic 2" -> absent
  from code.

Generators are fully deterministic: same spec in, same artifacts out.
"""

from .artifacts import FrameworkArtifacts
from . import spec as S

# Requirement -> implementation sketch used by every generator.
IMPL = {
    "R1": ("ingest_event", "validate schema (event_type, timestamp, payload); "
           "return 202 on success, 400 on malformed input"),
    "R2": ("verify_signature", "HMAC-SHA256 of raw body with tenant secret; "
           "401 on mismatch or missing header"),
    "R3": ("deliver_with_retry", "up to 5 attempts, exponential backoff "
           "base 2s with jitter"),
    "R4": ("check_rate_limit", "100 events/min per tenant; 429 + Retry-After"),
    "R5": ("dead_letter", "persist exhausted events with reason + attempts"),
    "R6": ("dedupe_event", "event_id dedupe window 24h; replay original result"),
    "R7": ("record_metrics", "structured logs + per-tenant counters "
           "delivered/failed/retried"),
    "R8": ("graceful_shutdown", "SIGTERM: stop listener, drain in-flight "
           "within 30s"),
}


def _code_fn(req_id, body_extra=""):
    fn, desc = IMPL[req_id]
    return (
        f"def {fn}(event, tenant):\n"
        f"    # REQ-{req_id}: {desc}\n"
        f"{body_extra}"
        f"    return handle_{fn}(event, tenant)  # implementation stub\n"
    )


def _test_fn(framework, req):
    fn, _ = IMPL[req.id]
    lines = [f"def test_{req.id.lower()}_{fn}():"]
    for ac in req.criteria:
        lines.append(f"    # REQ-{req.id} | {ac.id}: {ac.text}")
        lines.append(f"    assert check({fn!r}, {ac.id!r})")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- MetaGPT ---
def generate_metagpt() -> FrameworkArtifacts:
    """SOP pipeline: PM writes PRD, Architect designs, Engineer codes,
    QA agent re-verifies. Handoff loss: R8 ships without drain-timeout."""
    stages = ["PM: PRD", "Architect: system design", "Engineer: implement",
              "QA: re-verify each requirement"]
    code_parts = [
        '"""Webhook dispatcher -- generated via MetaGPT SOP pipeline."""',
        "# Role handoff chain: product_manager -> architect -> project_manager "
        "-> engineer -> qa_engineer",
    ]
    for req in S.REQUIREMENTS:
        if req.id == "R8":
            # Handoff loss: engineer implements shutdown flag but drops the
            # 30s drain-timeout nuance from the architect's design.
            code_parts.append(
                "def graceful_shutdown(event, tenant):\n"
                "    # REQ-R8: SIGTERM: stop listener (PARTIAL: drain timeout "
                "not enforced -- lost in architect->engineer handoff)\n"
                "    stop_listener()\n"
                "    return True\n"
            )
        else:
            code_parts.append(_code_fn(req.id))
    # QA agent adds an extra regression test per must-requirement.
    test_parts = ["# QA agent verification suite (re-verifies every requirement)"]
    for req in S.REQUIREMENTS:
        test_parts.append(_test_fn("metagpt", req))
        if req.priority == "must":
            test_parts.append(
                f"def test_{req.id.lower()}_qa_regression():\n"
                f"    # QA re-verification of {req.id}\n"
                f"    assert qa_verify({req.id!r})\n"
            )
    docs = (
        "# PRD + System Design (MetaGPT SOP)\n\n"
        "## PRD (product_manager)\nFeature: " + S.FEATURE_BLURB + "\n\n"
        "## System design (architect)\nModules: ingress, auth, dispatcher, "
        "retry, dlq, observability.\n\n"
        "## QA report (qa_engineer)\nAll requirements re-verified; R8 flagged "
        "PARTIAL (drain timeout missing).\n"
    )
    return FrameworkArtifacts(
        "metagpt", "\n".join(code_parts), "\n".join(test_parts), docs,
        pipeline_notes=" -> ".join(stages),
    )


# ---------------------------------------------------------------- Spec Kit --
def generate_speckit() -> FrameworkArtifacts:
    """constitution -> specify -> plan -> tasks -> implement.
    Strict traceability: every function cites its requirement IDs; a task
    checklist covers all 8 requirements. Tests are thin (1 per AC)."""
    stages = ["constitution", "specify", "plan", "tasks", "implement"]
    code_parts = [
        '"""Webhook dispatcher -- generated via spec-kit workflow."""',
        "# Traceability rule (constitution): every symbol cites its REQ-IDs.",
    ]
    for req in S.REQUIREMENTS:
        code_parts.append(_code_fn(req.id))
    test_parts = ["# Tests derived 1:1 from acceptance criteria (specify phase)"]
    for req in S.REQUIREMENTS:
        test_parts.append(_test_fn("speckit", req))
    checklist = "\n".join(
        f"- [x] T{i+1}: implement {r.id} ({r.title})"
        for i, r in enumerate(S.REQUIREMENTS)
    )
    docs = (
        "# Spec-Kit Artifacts\n\n## constitution.md\nTraceability is law: "
        "no code without REQ-ID citations.\n\n"
        "## spec.md\n" + S.FEATURE_BLURB + "\n\n"
        "## plan.md\nPhases: ingress -> auth -> dispatch -> resilience -> "
        "observability.\n\n## tasks.md\n" + checklist + "\n"
    )
    return FrameworkArtifacts(
        "speckit", "\n".join(code_parts), "\n".join(test_parts), docs,
        pipeline_notes=" -> ".join(stages),
    )


# -------------------------------------------------------------------- BMAD --
def generate_bmad() -> FrameworkArtifacts:
    """Agile method: sharded PRD/architecture docs, dev stories per epic.
    ACs copied verbatim into tests. R7 deferred to Epic 2 -> missing."""
    stages = ["sharded PRD", "architecture", "epic 1 stories", "dev stories"]
    code_parts = [
        '"""Webhook dispatcher -- generated via BMAD agile method."""',
        "# Epic 1: core dispatch. Epic 2 (observability, R7): DEFERRED.",
    ]
    for req in S.REQUIREMENTS:
        if req.id == "R7":
            code_parts.append(
                "# REQ-R7 DEFERRED to Epic 2 (observability) -- not implemented"
            )
        else:
            code_parts.append(_code_fn(req.id))
    test_parts = ["# Dev-story tests: acceptance criteria quoted verbatim"]
    for req in S.REQUIREMENTS:
        if req.id != "R7":
            test_parts.append(_test_fn("bmad", req))
    docs = (
        "# BMAD Sharded Docs\n\n## prd/epic-1.md\n" + S.FEATURE_BLURB + "\n\n"
        "## prd/epic-2.md (deferred)\nR7 observability.\n\n"
        "## stories/\nStory per requirement with AC quoted verbatim.\n"
    )
    return FrameworkArtifacts(
        "bmad", "\n".join(code_parts), "\n".join(test_parts), docs,
        pipeline_notes=" -> ".join(stages),
    )


GENERATORS = {
    "metagpt": generate_metagpt,
    "speckit": generate_speckit,
    "bmad": generate_bmad,
}

FRAMEWORK_BLURBS = {
    "metagpt": "MetaGPT — SOP multi-agent pipeline (PM/Architect/Engineer/QA)",
    "speckit": "Spec Kit — constitution/specify/plan/tasks/implement",
    "bmad": "BMAD — agile method, sharded docs, dev stories per epic",
}
