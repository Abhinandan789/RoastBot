"""tts.py - Text-to-speech. edge-tts (natural, free) or pyttsx3 (robotic, offline)."""

import os
import sys
import threading
import tempfile
import asyncio

ENABLE_TTS = os.environ.get("ENABLE_TTS", "true").lower() == "true"
TTS_BACKEND = os.environ.get("TTS_BACKEND", "pyttsx3")

PET_VOICE = {
    "droplet": {"rate": 185, "vol": 0.9},
    "smiley":  {"rate": 160, "vol": 0.9},
    "ghost":   {"rate": 130, "vol": 0.85},
    "robot":   {"rate": 205, "vol": 0.9},
    "cat":     {"rate": 175, "vol": 0.9},
}

# Edge-tts voice mapping (Microsoft neural voices — free via Edge)
EDGE_VOICES = {
    "droplet": "en-US-AnaNeural",
    "smiley":  "en-US-JennyNeural",
    "ghost":   "en-US-SteffanNeural",
    "robot":   "en-US-GuyNeural",
    "cat":     "en-US-AriaNeural",
}

_engine = None
_lock = threading.Lock()


def _get_engine():
    global _engine
    if _engine is None:
        import pyttsx3
        _engine = pyttsx3.init()
    return _engine


def _speak_pyttsx3(text, pet_name):
    """Offline robotic voice. No files, no internet, no popups."""
    with _lock:
        engine = _get_engine()
        cfg = PET_VOICE.get(pet_name, PET_VOICE["droplet"])
        engine.setProperty("rate", cfg["rate"])
        engine.setProperty("volume", cfg["vol"])

        for voice in engine.getProperty("voices"):
            vname = voice.name.lower()
            if "zira" in vname or "hazel" in vname or "natural" in vname:
                engine.setProperty("voice", voice.id)
                break

        engine.say(text)
        engine.runAndWait()


def _speak_edge_tts(text, pet_name):
    """
    Natural neural voice via Microsoft Edge (free).
    Generates MP3, plays it invisibly via playsound, then deletes it.
    """
    try:
        import edge_tts
        from playsound import playsound
    except ImportError as e:
        print(f"[TTS] Missing dependency ({e}), falling back to pyttsx3")
        _speak_pyttsx3(text, pet_name)
        return

    voice = EDGE_VOICES.get(pet_name, "en-US-JennyNeural")

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            mp3_path = f.name
        await communicate.save(mp3_path)

        # Play invisibly — playsound uses Windows MCI, no window popup
        try:
            playsound(mp3_path)
        except Exception as e:
            print(f"[TTS] playsound failed: {e}")
            # Last resort: open with default player (may show window)
            os.startfile(mp3_path)

        # Cleanup
        try:
            os.remove(mp3_path)
        except OSError:
            pass

    asyncio.run(_run())


def speak(text: str, pet_name: str = "droplet"):
    if not ENABLE_TTS:
        return

    def _run():
        try:
            if TTS_BACKEND == "edge-tts":
                _speak_edge_tts(text, pet_name)
            else:
                _speak_pyttsx3(text, pet_name)
        except Exception as e:
            print(f"[TTS] Error: {e}")

    threading.Thread(target=_run, daemon=True).start()