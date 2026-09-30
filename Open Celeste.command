#!/bin/sh
# Double-click on macOS, or run this script from Terminal.
cd "$(dirname "$0")" || exit 1
exec python3 -B dashboard.py --open
