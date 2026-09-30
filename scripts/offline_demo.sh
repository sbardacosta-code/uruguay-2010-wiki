#!/bin/sh
# Run after disconnecting all internet connections and starting local Ollama.
set -eu
cd "$(dirname "$0")/.."
printf 'Turn off Wi-Fi and unplug Ethernet before continuing.\n'
printf 'Confirm that this Mac is disconnected from the internet (type DISCONNECTED): '
read -r confirmation
if [ "$confirmation" != DISCONNECTED ]; then
  printf 'No offline run started.\n'
  exit 1
fi
run_folder="evidence/offline/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$run_folder"
network_observations() {
  date -u
  scutil --nwi || true
  wifi_device=$(networksetup -listallhardwareports | awk '/Hardware Port: (Wi-Fi|AirPort)/ {getline; print $2; exit}')
  if [ -n "$wifi_device" ]; then
    networksetup -getairportpower "$wifi_device" || true
  else
    printf 'No Wi-Fi interface identified; inspect all active connections manually.\n'
  fi
}
{
  printf 'User attestation: disconnected from internet\n'
  network_observations
  printf '\nRuntime identity\n'
  ./wiki status
} > "$run_folder/environment.txt" 2>&1
# -x makes executed commands visible. Keep each attempt, including failures.
/usr/bin/script -q "$run_folder/terminal.txt" /bin/sh -x scripts/offline_commands.sh
network_observations > "$run_folder/network-after.txt" 2>&1
printf '\nSaved %s. Capture terminal and network settings before reconnecting.\n' "$run_folder"
printf 'Inspect the transcript: recording completion alone does not mean every test passed.\n'
