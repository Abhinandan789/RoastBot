"""sounds.py - Tiny non-blocking click for the bubble typing effect."""

import sys
import threading


def play_typing_click():
    """Short beep, mimicking a mechanical-keyboard tick. Windows-only;
    silently no-ops elsewhere (e.g. if this ever runs under Termux)."""
    if sys.platform != "win32":
        return

    import winsound
    threading.Thread(target=lambda: winsound.Beep(1400, 8), daemon=True).start()