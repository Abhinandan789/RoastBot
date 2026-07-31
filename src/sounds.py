"""sounds.py - Tiny non-blocking click for the bubble typing effect."""

import sys
import threading


def play_typing_click():
    """Short mechanical-keyboard tick. Windows-only; silent elsewhere.
    Skipped while TTS is speaking - winsound.Beep() and SAPI (pyttsx3)
    fight over the same Windows audio session, and Beep() wins,
    cutting the voice off mid-word."""
    if sys.platform != "win32":
        return

    from src.tts import is_speaking
    if is_speaking():
        return

    import winsound

    def _beep():
        try:
            winsound.Beep(1200, 45)
        except Exception:
            try:
                winsound.MessageBeep(winsound.MB_OK)
            except Exception:
                pass

    threading.Thread(target=_beep, daemon=True).start()