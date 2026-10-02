"""Artifact containers produced by each framework pipeline."""

from dataclasses import dataclass, field


@dataclass
class FrameworkArtifacts:
    framework: str          # "metagpt" | "speckit" | "bmad"
    code: str               # generated implementation (Python source)
    tests: str              # generated test module (Python source)
    docs: str               # generated design/plan/story docs (markdown)
    pipeline_notes: str = ""  # which pipeline stages ran, in order


@dataclass
class FidelityScores:
    framework: str
    requirement_coverage: float   # 0..1  requirements cited in code
    traceability: float           # 0..1  requirements cited in code AND tests
    ac_alignment: float           # 0..1  acceptance criteria quoted in tests
    test_density: float           # tests per requirement (raw)
    test_density_norm: float      # 0..1  normalized test density
    doc_completeness: float       # 0..1  doc sections present
    fidelity_score: float         # 0..100 weighted composite
