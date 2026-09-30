#!/bin/sh
set -eu
./wiki --help
./wiki ingest vault/raw --source S07 --force
./wiki ask "What were Uruguay's results in the group stage of the 2010 World Cup, and how many points did they finish with?" --mode local
./wiki ask "How was Uruguay's match against Ghana decided, and what did Muslera and Abreu do?" --mode local
./wiki ask "Who did Uruguay play after the quarter-finals, and where did they finish?" --mode local
./wiki ask "What did Diego Forlan eat for breakfast on the day Uruguay played Ghana in the 2010 World Cup?" --mode local
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
