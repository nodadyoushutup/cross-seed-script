#!/bin/bash
# tail_job_logs.sh
# Show the last 10 lines of logs/info.current.log across multiple cross-seed directories

# Base directory
BASE_DIR="/mnt/epool/config"

# List of subdirectories
SUBDIRS=(
  "cross-seed-ab"
  "cross-seed-ant"
  "cross-seed-ath"
  "cross-seed-bhd"
  "cross-seed-blu"
  "cross-seed-cg"
  "cross-seed-hdb"
  "cross-seed-kg"
  "cross-seed-sc"
)

# Loop through each directory and check for log file
for dir in "${SUBDIRS[@]}"; do
  LOG_PATH="$BASE_DIR/$dir/logs/info.current.log"
  if [[ -f "$LOG_PATH" ]]; then
    echo "===== $dir ====="
    tail -n 15 "$LOG_PATH"
    echo
  else
    echo "⚠️  Log file not found: $LOG_PATH"
    echo
  fi
done
