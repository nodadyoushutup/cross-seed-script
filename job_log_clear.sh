#!/bin/bash
# clear_job_logs.sh
# Deletes all rows from job_log table across multiple cross-seed databases

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

# Loop through each directory and clear the job_log table
for dir in "${SUBDIRS[@]}"; do
  DB_PATH="$BASE_DIR/$dir/cross-seed.db"
  if [[ -f "$DB_PATH" ]]; then
    echo "Clearing job_log in $DB_PATH..."
    sqlite3 "$DB_PATH" "DELETE FROM job_log;" && echo "✅ Cleared $dir"
  else
    echo "⚠️  Database not found: $DB_PATH"
  fi
done

echo "Done."
