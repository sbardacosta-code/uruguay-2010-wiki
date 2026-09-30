#!/bin/sh
# Run only after disconnecting Wi-Fi/Ethernet and starting the local Ollama server.
set -eu
cd "$(dirname "$0")/.."
mkdir -p evidence/offline
printf 'Turn off Wi-Fi and unplug Ethernet before continuing.\n'
printf 'Confirm that this Mac is disconnected from the internet (type DISCONNECTED): '
read -r confirmation
if [ "$confirmation" != DISCONNECTED ]; then
  printf 'No offline run started.\n'
  exit 1
fi
# Store OS network observations as well as the user's attestation.
{
  date -u
  printf '\nUser attestation: disconnected from internet\n'
  scutil --nwi
  networksetup -getairportpower en0
  printf '\nRuntime identity\n'
  ./wiki status
} > evidence/offline/environment.txt 2>&1
# macOS script records real terminal output to a file. Every command starts a new CLI.
/usr/bin/script -q evidence/offline/terminal.txt /bin/sh scripts/offline_commands.sh
printf '\nSaved evidence/offline/terminal.txt. Capture the terminal and network settings before reconnecting.\n'
