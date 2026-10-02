#!/usr/bin/env python3
"""Run the SDLC frameworks spec-to-code fidelity benchmark.

Generates deterministic methodology-driven artifacts for MetaGPT, Spec Kit
and BMAD against the same feature spec, scores them, and writes
results/results.json + results/report.md.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sdlc_eval import frameworks, report
from sdlc_eval.scorer import rank, score

OUT = ROOT / "results"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    artifacts = [gen() for gen in frameworks.GENERATORS.values()]
    scores = [score(a) for a in artifacts]
    ranked = rank(scores)

    (out / "results.json").write_text(report.to_json(ranked))
    (out / "report.md").write_text(report.render_report(ranked, artifacts))

    print(report.render_table(ranked))
    print(f"\nWrote {out / 'results.json'} and {out / 'report.md'}")


if __name__ == "__main__":
    main()
