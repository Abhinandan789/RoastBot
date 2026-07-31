"""tts.py - Text-to-speech. edge-tts (natural, free) or pyttsx3 (robotic, offline)."""

import os
import sys
import threading
import tempfile
import asyncio
import time

ENABLE_TTS = os.environ.get("ENABLE_TTS", "true").lower() == "true"
TTS_BACKEND = os.environ.get("TTS_BACKEND", "pyttsx3")

PET_VOICE = {
    "droplet": {"rate": 185, "vol": 0.9},
    "smiley":  {"rate": 160, "vol": 0.9},
    "ghost":   {"rate": 130, "vol": 0.85},
    "robot":   {"rate": 205, "vol": 0.9},
    "cat":     {"rate": 175, "vol": 0.9},
    "smiley2": {"rate": 165, "vol": 0.9},
}

EDGE_VOICES = {
    "droplet": "en-US-AnaNeural",
    "smiley":  "en-US-JennyNeural",
    "ghost":   "en-US-SteffanNeural",
    "robot":   "en-US-GuyNeural",
    "cat":     "en-US-AriaNeural",
    "smiley2": "en-US-JennyNeural",
}

_engine = None
_lock = threading.Lock()
_last_spoken = {"text": None, "time": 0}

_speaking = {"active": False}
_speaking_lock = threading.Lock()


def is_speaking():
    with _speaking_lock:
        return _speaking["active"]


def _set_speaking(value):
    with _speaking_lock:
        _speaking["active"] = value

def _get_engine():
    global _engine
    if _engine is None:
        import pyttsx3
        _engine = pyttsx3.init()
    return _engine


def _speak_pyttsx3(text, pet_name):
    """Offline robotic voice."""
    print(f"[TTS] pyttsx3 speaking for {pet_name}: {text[:60]}...")
    with _lock:
        try:
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
            print("[TTS] pyttsx3 finished.")
        except Exception as e:
            print(f"[TTS] pyttsx3 ERROR: {e}")


def _speak_edge_tts(text, pet_name):
    """Natural neural voice via Microsoft Edge (free)."""
    print(f"[TTS] edge-tts speaking for {pet_name}: {text[:60]}...")
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
        try:
            playsound(mp3_path)
            print("[TTS] edge-tts finished.")
        except Exception as e:
            print(f"[TTS] playsound failed: {e}")
            os.startfile(mp3_path)
        try:
            os.remove(mp3_path)
        except OSError:
            pass

    try:
        asyncio.run(_run())
    except Exception as e:
        print(f"[TTS] edge-tts ERROR: {e}")


def speak(text: str, pet_name: str = "droplet"):
    if not ENABLE_TTS:
        print("[TTS] Disabled via ENABLE_TTS env var.")
        return

    # Deduplicate: don't re-speak the same text within 5 seconds
    now = time.time()
    with _lock:
        if text == _last_spoken["text"] and now - _last_spoken["time"] < 5:
            print(f"[TTS] Skipping duplicate speech: {text[:60]}...")
            return
        _last_spoken["text"] = text
        _last_spoken["time"] = now

    def _run():
        _set_speaking(True)
        try:
            if TTS_BACKEND == "edge-tts":
                _speak_edge_tts(text, pet_name)
            else:
                _speak_pyttsx3(text, pet_name)
        except Exception as e:
            print(f"[TTS] Error: {e}")
        finally:
            _set_speaking(False)
    
    threading.Thread(target=_run, daemon=True).start()
