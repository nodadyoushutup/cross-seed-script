from pathlib import Path

# Base directory containing app configurations
BASE_DIR = Path('/mnt/epool/config')

# Names of the cross-seed applications to monitor
APPS = [
    'cross-seed-ab',
    'cross-seed-ant',
    'cross-seed-ath',
    'cross-seed-bhd',
    # 'cross-seed-blu',
    'cross-seed-cg',
    'cross-seed-hdb',
    'cross-seed-kg',
]

# Interval (in seconds) between log scans
SCAN_INTERVAL = 10

# Delay (in seconds) before restarting each application after a failure
# Set the value for each app as desired (defaults here are 60 minutes)
RESTART_DELAYS = {
    'cross-seed-ab': 60 * 15,
    'cross-seed-ant': 60 * 15,
    'cross-seed-ath': 60 * 15,
    'cross-seed-bhd': 60 * 15,
    'cross-seed-blu': 60 * 15,
    'cross-seed-cg': 60 * 15,
    'cross-seed-hdb': 60 * 15,
    'cross-seed-kg': 60 * 15,
}
