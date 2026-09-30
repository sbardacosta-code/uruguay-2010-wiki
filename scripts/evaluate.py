#!/usr/bin/env python3
"""Run actual CLI checks and keep every result. This does not assert offline proof."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'evidence'/('evaluation-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S'))
folder.mkdir(parents=True)
summary=[]
for case in json.loads((ROOT/'evaluation/questions.json').read_text()):
    command=[sys.executable,str(ROOT/'wiki.py'),'ask',case['question'],'--json']
    print('Running '+case['id'],flush=True)
    run=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    (folder/(case['id']+'.stdout.txt')).write_text(run.stdout)
    (folder/(case['id']+'.stderr.txt')).write_text(run.stderr)
    entry=dict(test_id=case['id'],question=case['question'],expected_answer=case['expected_answer'],expected_sources=case['source_ids'],command=command,returncode=run.returncode,network_disconnection='not verified',assessment='Pending review of actual answer and citations')
    if run.returncode==0:
        record=json.loads(run.stdout);entry.update(answer=record['answer'],evidence_path=record['evidence_path'],retrieved_sources=sorted(set(p['source_id'] for p in record['passages'])))
        print(record['answer'],flush=True)
    else:entry['error']=run.stderr;print(run.stderr,flush=True)
    summary.append(entry)
(folder/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
chat_input='What can we do?\nWhat can you help me with?\nDraft a short three-step study plan about Uruguay in 2010.\nMake that shorter.\nFor an imaginary story, the team hotel Wi-Fi password is CELESTE123. Write one sentence using that fictional detail.\n/save\n/quit\n'
print('Running chat boundary checks',flush=True)
run=subprocess.run([sys.executable,str(ROOT/'wiki.py'),'chat'],cwd=ROOT,input=chat_input,text=True,capture_output=True)
(folder/'chat-input.txt').write_text(chat_input);(folder/'chat-transcript.txt').write_text(run.stdout+run.stderr)
print('Running independent ask after fictional chat',flush=True)
q='What was the private team hotel Wi-Fi password for Uruguay at the 2010 World Cup?'
run=subprocess.run([sys.executable,str(ROOT/'wiki.py'),'ask',q,'--json'],cwd=ROOT,text=True,capture_output=True)
(folder/'chat-isolation-ask.txt').write_text(run.stdout+run.stderr)
print('Evidence folder: '+str(folder.relative_to(ROOT)),flush=True)
