# sdlc-frameworks-eval

**Spec-to-code fidelity benchmark: MetaGPT vs Spec Kit vs BMAD on one fixed feature.**

All three SDLC agent frameworks receive the *same* feature spec — a
multi-tenant webhook event dispatcher with 8 requirements (R1–R8) and 21
acceptance criteria — and the harness measures how faithfully each
methodology turns spec into code, tests, and docs.

## Methodology

The frameworks are **simulated deterministically from their published
methodologies** (no LLM calls — this measures *methodology* differences,
not live runs):

| Framework | Pipeline | Encoded trait |
|---|---|---|
| **MetaGPT** | SOP: PM → Architect → Engineer → QA | QA agent re-verifies every requirement (high test density); R8 ships PARTIAL — drain-timeout nuance lost in the Architect→Engineer handoff |
| **Spec Kit** | constitution → specify → plan → tasks → implement | Strict traceability: every function cites REQ-IDs; task checklist covers all 8; tests are thin (1 per acceptance criterion) |
| **BMAD** | Sharded PRD/architecture, dev stories per epic | Acceptance criteria quoted verbatim in tests; R7 (observability) **deferred to Epic 2** — absent from code |

## Fidelity dimensions

- **Requirement coverage** — requirements with a real implementation in code
- **Traceability** — requirements cited in *both* code and tests
- **AC alignment** — acceptance criteria quoted verbatim in tests
- **Test density** — tests per requirement (saturates at 3)
- **Doc completeness** — expected methodology docs present

Composite: `35·coverage + 25·traceability + 20·AC alignment + 10·test density + 10·docs`

## Results (2026-10-02)

| Framework | Fidelity | Coverage | Traceability | AC alignment | Tests/req |
|---|---|---|---|---|---|
| MetaGPT | **95.4** | 100% | 100% | 100% | 1.62 |
| Spec Kit | **93.3** | 100% | 100% | 100% | 1.00 |
| BMAD | **83.6** | 88% | 88% | 91% | 0.88 |

Takeaway: the QA re-verification loop (MetaGPT) wins on test rigor; plan-first
discipline (Spec Kit) wins on traceability; story-driven development (BMAD)
quotes acceptance criteria best but pays for deferring cross-cutting
requirements like observability.

## Run it

```bash
pip install -r requirements.txt
python run.py                 # prints the ranking table
python -m pytest tests/ -q    # 22 tests
```

Outputs: `results/results.json` and `results/report.md` (deterministic —
every run produces identical artifacts and scores).

## Layout

```
sdlc_eval/
  spec.py         # canonical feature spec: 8 requirements, 21 ACs
  frameworks.py   # methodology-driven deterministic artifact generators
  scorer.py       # static-analysis fidelity scorer
  report.py       # markdown + JSON report rendering
  artifacts.py    # dataclasses
run.py            # benchmark entrypoint
tests/            # 22 tests (spec integrity, generator traits, scorer, reproducibility)
results/          # generated report + JSON
```

## License

MIT — see [LICENSE](LICENSE).
