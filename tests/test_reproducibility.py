"""End-to-end reproducibility: run.py output is stable across runs."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(outdir):
    r = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--out", str(outdir)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    return json.loads((outdir / "results.json").read_text())


def test_two_runs_identical(tmp_path):
    a = _run(tmp_path / "a")
    b = _run(tmp_path / "b")
    assert a == b


def test_report_md_written(tmp_path):
    _run(tmp_path / "r")
    md = (tmp_path / "r" / "report.md").read_text()
    assert "# SDLC Frameworks Eval" in md
    assert "## Fidelity ranking" in md
