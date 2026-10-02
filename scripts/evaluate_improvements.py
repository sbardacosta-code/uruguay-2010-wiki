#!/usr/bin/env python3
"""Keep supplemental CLI outputs separate from the unchanged offline recording.

A zero exit code reports successful execution only. Source-based assessments
are written separately after inspecting actual outputs; this is not offline proof.
"""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
folder = (
    ROOT
    / "evidence"
    / ("improvements-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
)
folder.mkdir(parents=True)
cases = json.loads((ROOT / "evaluation/questions.json").read_text()) + json.loads(
    (ROOT / "evaluation/improvement-questions.json").read_text()
)
summary = []
for case in cases:
    command = [sys.executable, str(ROOT / "wiki.py"), "ask", case["question"], "--json"]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (folder / (case["id"] + ".stdout.json")).write_text(run.stdout)
    (folder / (case["id"] + ".stderr.txt")).write_text(run.stderr)
    entry = dict(
        id=case["id"],
        question=case["question"],
        expected=case.get("expected", case.get("expected_answer")),
        returncode=run.returncode,
        network_disconnection="not verified",
        assessment="Pending source review",
    )
    if run.returncode == 0:
        result = json.loads(run.stdout)
        entry.update(answer=result["answer"], evidence_path=result["evidence_path"])
    else:
        entry["error"] = run.stderr
    summary.append(entry)
    (folder / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )
    print(case["id"] + ": " + entry.get("answer", entry.get("error", "")), flush=True)
print("Evidence: " + str(folder.relative_to(ROOT)), flush=True)
sys.exit(1 if any(entry["returncode"] for entry in summary) else 0)
