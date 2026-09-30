#!/usr/bin/env python3
"""Run the original four questions verbatim, visibly, in separate CLI processes."""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for case in json.loads((root / 'evaluation/questions.json').read_text()):
    print('\n' + case['id'] + ': ' + case['question'], flush=True)
    subprocess.run(['./wiki', 'ask', case['question'], '--mode', 'local'], cwd=root, check=True)
