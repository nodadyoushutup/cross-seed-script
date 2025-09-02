from pathlib import Path

# Base directory containing app configurations
BASE_DIR = Path('/mnt/epool/config')

# Names of the cross-seed applications to monitor
APPS = [
    'cross-seed-ab',
    'cross-seed-ant',
    'cross-seed-ath',
    'cross-seed-bhd',
    'cross-seed-blu',
    'cross-seed-cg',
    'cross-seed-hdb',
    'cross-seed-kg',
]

# Interval (in seconds) between log scans
SCAN_INTERVAL = 10

# Delay (in seconds) before restarting an application after a failure
RESTART_DELAY = 60 * 60  # 60 minutes
