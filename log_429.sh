#!/bin/bash
# log_429.sh
# Checks for isolated "429" errors in logs/info.current.log across cross-seed directories

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
)

found_any=false

# Loop through each directory and check for 429 errors
for dir in "${SUBDIRS[@]}"; do
  LOG_PATH="$BASE_DIR/$dir/logs/info.current.log"
  if [[ -f "$LOG_PATH" ]]; then
    if grep -Eq '(^|[^[:alnum:]_])429([^[:alnum:]_]|$)' "$LOG_PATH"; then
      echo "⚠️  429 errors found in $dir:"
      grep -En '(^|[^[:alnum:]_])429([^[:alnum:]_]|$)' "$LOG_PATH"
      echo
      found_any=true
    else
      echo "✅ No 429 errors in $dir"
    fi
  else
    echo "⚠️  Log file not found: $LOG_PATH"
  fi
done

if [ "$found_any" = false ]; then
  echo "🎉 No 429 errors found in any logs."
fi
