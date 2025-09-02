#!/bin/bash
# app_stop.sh
# Stop TrueNAS SCALE apps (Dragonfish 24.04) by scaling them to 0 replicas via midclt.

set -euo pipefail

APPS=(
  "cross-seed-ab"
  "cross-seed-ant"
  "cross-seed-ath"
  "cross-seed-bhd"
  "cross-seed-blu"
  "cross-seed-cg"
  "cross-seed-hdb"
  "cross-seed-kg"
)

have() { command -v "$1" >/dev/null 2>&1; }

if ! have midclt; then
  echo "ERROR: 'midclt' not found on PATH. Run this on the TrueNAS SCALE host shell."
  exit 2
fi

stop_app() {
  local app="$1"
  echo "===== Stopping ${app} (scaling to 0) ====="
  # Run as a job so the command blocks until completion and returns proper status
  if midclt call -job chart.release.scale "$app" '{"replica_count": 0}'; then
    echo "✅ ${app}: scaled to 0"
  else
    echo "❌ ${app}: failed to scale to 0"
    return 1
  fi
}

overall_rc=0
for app in "${APPS[@]}"; do
  if ! stop_app "$app"; then
    overall_rc=1
  fi
done

exit "$overall_rc"
