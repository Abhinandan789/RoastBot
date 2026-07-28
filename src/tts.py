"""
tts.py - Offline text-to-speech using pyttsx3 (Windows built-in voices).

pyttsx3's engine is not safe to run concurrently from multiple threads -
calling runAndWait() while a previous call is still in progress raises
RuntimeError. A lock serializes speak() calls so overlapping roasts
(or rapid manual triggers) queue instead of crashing.
"""

import threading
import pyttsx3

PET_VOICE = {
    "droplet": {"rate": 185, "vol": 0.9},
    "smiley": {"rate": 160, "vol": 0.9},
    "smiley2": {"rate": 165, "vol": 0.9},
    "ghost": {"rate": 130, "vol": 0.85},
    "robot": {"rate": 205, "vol": 0.9},
    "cat": {"rate": 175, "vol": 0.9},
}

_engine = None
_speak_lock = threading.Lock()


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
    return _engine


def speak(text: str, pet_name: str = "droplet"):
    """Speak a roast aloud in a background thread. Safe to call even if
    a previous speak() is still finishing - it will wait its turn."""

    def _run():
        with _speak_lock:
            engine = _get_engine()
            cfg = PET_VOICE.get(pet_name, PET_VOICE["droplet"])
            engine.setProperty("rate", cfg["rate"])
            engine.setProperty("volume", cfg["vol"])

            for voice in engine.getProperty("voices"):
                name = voice.name.lower()
                if "zira" in name or "hazel" in name or "natural" in name:
                    engine.setProperty("voice", voice.id)
                    break

            engine.say(text)
            engine.runAndWait()

    threading.Thread(target=_run, daemon=True).start()