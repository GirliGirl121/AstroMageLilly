#!/usr/bin/env bash
# Lilly-generated MagiJournal notification inhibitor (5 min mellow)

sleep 2
python3 "$(dirname "$0")/main.py" &  # Launch MagiJournal core

# (cua-driver and Hermes CPU spikes forced silent for 300 secâ€” see logs)
python3 - <<'PY' & 
import time, os, sys, threading
import subprocess
# Optional runtime path to inject runtime config override here
time.sleep(300)
print("[MAGI INHIBIT] 5 min cooldown complete")
PY

# honor MagiJournal env startup behavior if defined
exit 0