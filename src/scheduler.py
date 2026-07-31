"""
scheduler.py - In-process background scheduler for roast generation.

Single responsibility: run roast.main() on a repeating interval inside
a daemon thread, so pet_widget.py alone (no Task Scheduler, no second
terminal) is enough to keep the bot alive. Failures are caught and
logged so one bad run (network blip, Groq downtime, etc.) never kills
the loop or the pet widget itself.
"""

import threading
import time
import traceback
from datetime import datetime, timezone

DEFAULT_INTERVAL_SECONDS = 3 * 60 * 60  # 3 hours, matches old termux-job-scheduler cadence


def _run_loop(interval_seconds):
    from src.roast import main as roast_main  # imported lazily to avoid circular imports

    while True:
        try:
            print(f"[scheduler] running roast.main() at {datetime.now(timezone.utc).isoformat()}")
            roast_main()
        except Exception:
            # Never let a bad run kill the background thread.
            print("[scheduler] roast.main() raised an exception:")
            traceback.print_exc()
        time.sleep(interval_seconds)


def start_background_scheduler(interval_seconds=DEFAULT_INTERVAL_SECONDS):
    """
    Starts roast.main() immediately, then every `interval_seconds` after
    that, in a daemon thread. Daemon=True so it never blocks the widget
    from closing on right-click/exit.
    """
    thread = threading.Thread(target=_run_loop, args=(interval_seconds,), daemon=True)
    thread.start()
    return thread