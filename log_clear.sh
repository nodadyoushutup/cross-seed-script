#!/bin/bash
# clear_log_dirs.sh
# Clears all log files inside logs/ directory for each cross-seed instance

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

# Loop through each directory and clear logs
for dir in "${SUBDIRS[@]}"; do
  LOG_DIR="$BASE_DIR/$dir/logs"
  if [[ -d "$LOG_DIR" ]]; then
    echo "Clearing logs in $LOG_DIR..."
    rm -rf "$LOG_DIR" && echo "✅ Cleared $dir"
  else
    echo "⚠️  Log directory not found: $LOG_DIR"
  fi
done

echo "Done."
