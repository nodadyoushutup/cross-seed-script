import logging
import threading
import time
import re
from datetime import datetime
from pathlib import Path

from config import BASE_DIR, APPS, SCAN_INTERVAL
from app_manager import restart_procedure

logger = logging.getLogger(__name__)

# Active restart threads keyed by app name
_active_threads: dict[str, threading.Thread] = {}
_lock = threading.Lock()

# Regular expression to match isolated "429" codes or "rate limited" messages
ERROR_RE = re.compile(
    r'(^|[^[:alnum:]_])429([^[:alnum:]_]|$)|rate limited|rate limit|rate limiting', re.IGNORECASE
)


def check_logs() -> None:
    """Scan log files for each application and trigger restarts if needed."""
    for app in APPS:
        with _lock:
            if app in _active_threads:
                continue
        log_file = BASE_DIR / app / "logs" / "info.current.log"
        if not log_file.exists():
            logger.warning("Log file not found for %s: %s", app, log_file)
            continue
        try:
            with log_file.open() as fh:
                for line in fh:
                    if ERROR_RE.search(line):
                        logger.warning("Rate limit error detected for %s", app)
                        t = threading.Thread(target=_worker, args=(app,), daemon=True)
                        with _lock:
                            _active_threads[app] = t
                        t.start()
                        break
        except Exception:
            logger.exception("Failed reading log for %s", app)


def _worker(app: str) -> None:
    try:
        restart_procedure(app)
    finally:
        with _lock:
            _active_threads.pop(app, None)


def main() -> None:
    """Entry point for the log monitoring daemon."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("monitor_logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"monitor_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    logger.info("Starting log monitor")
    while True:
        logger.info("Scanning logs")
        check_logs()
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
