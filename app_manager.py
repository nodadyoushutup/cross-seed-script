import json
import logging
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

from config import BASE_DIR, RESTART_DELAY

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

    The ``chart.release.get_instance`` midclt call is expected to return a JSON
    object describing the release.  In some failure cases midclt may instead
    return a plain string (for example an error message).  Attempting to treat
    that string like a dictionary previously resulted in an ``AttributeError``
    bubbling up to the monitor thread.

    To make the monitor robust we defensively parse the output and ensure we
    only access the "scale" field when a mapping object is returned.  Any
    unexpected output is logged and ``-1`` is returned to signal an unknown
    scale.
    """
    proc = _run_midclt(["call", "chart.release.get_instance", app])
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        logger.error("Invalid JSON from midclt for %s: %s", app, proc.stdout.strip())
        return -1
    if not isinstance(data, dict):
        logger.error("Unexpected response from midclt for %s: %s", app, data)
        return -1
    return data.get("status", {}).get("scale", -1)


def wait_for_stop(app: str, timeout: int = 60) -> bool:
    """Wait until an application reports scale 0."""
    end = time.time() + timeout
    while time.time() < end:
        if _get_app_scale(app) == 0:
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
    logger.info("Waiting %d seconds before restarting %s", RESTART_DELAY, app)
    time.sleep(RESTART_DELAY)
    start_app(app)
    logger.info("Restarted %s", app)
