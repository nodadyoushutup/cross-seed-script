import json
import logging
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from config import BASE_DIR, RESTART_DELAYS

logger = logging.getLogger(__name__)


def _run_midclt(args):
    """Run a midclt command and return completed process."""
    return subprocess.run(
        ["midclt", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def stop_app(app: str) -> None:
    """Scale an application to 0 replicas."""
    logger.info("Stopping %s", app)
    _run_midclt(["call", "-job", "chart.release.scale", app, '{"replica_count": 0}'])


def start_app(app: str) -> None:
    """Scale an application to 1 replica."""
    logger.info("Starting %s", app)
    _run_midclt(["call", "-job", "chart.release.scale", app, '{"replica_count": 1}'])


def _get_app_scale(app: str) -> int:
    """Return the current replica count for an application.

    The ``chart.release.get_instance`` midclt call should emit a JSON object
    describing the release.  Historically we expected this structure to contain
    ``{"status": {"scale": <int>}}`` but on some TrueNAS versions the
    ``status`` field is simply a string (e.g. ``"STOPPED"``) and the desired
    replica count lives in ``pod_status.desired``.  When the output deviates from
    our expectations we defensively handle it and return ``-1`` to indicate an
    unknown scale.
    """
    proc = _run_midclt(["call", "chart.release.get_instance", app])
    logger.info(
        "midclt get_instance output for %s: %s", app, proc.stdout.strip()
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        logger.error("Invalid JSON from midclt for %s: %s", app, proc.stdout.strip())
        return -1
    if not isinstance(data, dict):
        logger.error("Unexpected response from midclt for %s: %s", app, data)
        return -1

    status_info = data.get("status")
    if isinstance(status_info, dict):
        return status_info.get("scale", -1)

    pod_status = data.get("pod_status")
    if isinstance(pod_status, dict):
        return pod_status.get("desired", -1)

    logger.error("Could not determine scale for %s from midclt response", app)
    return -1


def wait_for_stop(app: str, timeout: int = 60) -> bool:
    """Wait until an application reports scale 0."""
    end = time.time() + timeout
    while time.time() < end:
        scale = _get_app_scale(app)
        logger.debug("Current scale for %s: %s", app, scale)
        if scale == 0:
            return True
        time.sleep(2)
    return False


def clear_job_log(app: str) -> None:
    """Delete all rows from job_log table for an application."""
    db_path = BASE_DIR / app / "cross-seed.db"
    if not db_path.exists():
        logger.warning("Database not found for %s: %s", app, db_path)
        return
    logger.info("Clearing job_log for %s", app)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM job_log")
    finally:
        conn.close()


def clear_logs(app: str) -> None:
    """Remove logs directory for an application."""
    log_dir = BASE_DIR / app / "logs"
    if not log_dir.exists():
        logger.warning("Logs directory not found for %s: %s", app, log_dir)
        return
    logger.info("Removing logs in %s", log_dir)
    shutil.rmtree(log_dir)


def restart_procedure(app: str) -> None:
    """Full restart procedure for an application."""
    stop_app(app)
    if not wait_for_stop(app):
        logger.error("Failed to confirm %s has stopped", app)
        return
    clear_job_log(app)
    clear_logs(app)
    delay = RESTART_DELAYS.get(app, 60 * 60)
    logger.info("Waiting %d seconds before restarting %s", delay, app)
    time.sleep(delay)
    start_app(app)
    logger.info("Restarted %s", app)
