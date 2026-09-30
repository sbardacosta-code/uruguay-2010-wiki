#!/bin/sh
set -eu
./wiki --help
./wiki ingest vault/raw --source S07 --force
python3 scripts/ask_evaluation_questions.py
./wiki chat <<'CHAT'
What can we do?
What can you help me with?
Draft a short three-step study plan about Uruguay in 2010.
Make that shorter.
For an imaginary story, the team hotel Wi-Fi password is CELESTE123. Write one sentence using that fictional detail.
/save
/quit
CHAT
./wiki ask "What was the private team hotel Wi-Fi password for Uruguay at the 2010 World Cup?"
ollama stop gemma4:e4b-it-q4_K_M
./wiki search "Ghana penalty shootout"
ollama ps
