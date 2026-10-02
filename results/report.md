# SDLC Frameworks Eval — webhook-dispatcher (2026-10-02)

Feature: A multi-tenant webhook event dispatcher: accept events via HTTP, verify signatures, enforce rate limits, deliver with retries, and quarantine permanently failing events.
Requirements: 8 (22 acceptance criteria)

## Fidelity ranking

| Framework | Fidelity | Coverage | Traceability | AC alignment | Tests/req | Docs |
|---|---|---|---|---|---|---|
| MetaGPT | 95.4 | 100% | 100% | 100% | 1.62 | 100% |
| Spec Kit | 93.3 | 100% | 100% | 100% | 1.00 | 100% |
| BMAD | 83.6 | 88% | 88% | 91% | 0.88 | 100% |

## Pipeline notes

- **MetaGPT — SOP multi-agent pipeline (PM/Architect/Engineer/QA)**: PM: PRD -> Architect: system design -> Engineer: implement -> QA: re-verify each requirement
- **Spec Kit — constitution/specify/plan/tasks/implement**: constitution -> specify -> plan -> tasks -> implement
- **BMAD — agile method, sharded docs, dev stories per epic**: sharded PRD -> architecture -> epic 1 stories -> dev stories

## Reading the results

- **Coverage**: share of R1–R8 with a real implementation in generated code.
- **Traceability**: requirements cited in both code and tests.
- **AC alignment**: acceptance criteria quoted verbatim in tests.
- Methodology simulations are deterministic; no LLM calls are made.
