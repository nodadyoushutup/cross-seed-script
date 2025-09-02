# cross-seed-script

Utilities for managing cross-seed applications on TrueNAS.  The Python
`monitor.py` script watches log files for HTTP 429 errors and
automatically restarts affected applications.

## Usage

```bash
python monitor.py
```

Logs from each run are written to the console and also saved under
`monitor_logs/` with a timestamped filename (e.g.
`monitor_logs/monitor_20240101_120000.log`).

The script scans each application's log every 10 seconds.  When a 429
error is detected a background thread will:

1. Stop the application via `midclt`.
2. Confirm the app is stopped.
3. Clear the `job_log` table in `cross-seed.db`.
4. Remove the `logs/` directory for a fresh start.
5. Wait a configurable delay (default 60 minutes) before restarting the application.

Restart delays for each application are configured in `config.py` via the
`RESTART_DELAYS` dictionary.
