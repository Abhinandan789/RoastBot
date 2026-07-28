"""sounds.py - Tiny non-blocking click for the bubble typing effect."""

import sys
import threading


def play_typing_click():
    """Short mechanical-keyboard tick. Windows-only; silent elsewhere."""
    if sys.platform != "win32":
        return

    import winsound

    def _beep():
        try:
            # 45ms is the sweet spot — audible but not annoying
            winsound.Beep(1200, 45)
        except Exception:
            # Fallback if Beep is blocked (some Windows configs)
            try:
                winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

    threading.Thread(target=_beep, daemon=True).start()