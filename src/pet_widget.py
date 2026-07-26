"""
pet_widget.py - The floating desktop pet window.

Single responsibility: manage the Tkinter window lifecycle, run the
continuous animation loop, poll pet_state.json for changes, and trigger
the auto-popup speech bubble when a new roast arrives. Drawing itself is
delegated entirely to pet_animations.py. History display is delegated
to a Toplevel window that reads directly from db.py (added in Stage 4).

This process is independent from roast.py - it only reads pet_state.json,
never writes to it, and never calls the GitHub/Groq APIs directly.
"""

import json
import os
import tkinter as tk

from src.config import PET_STATE_FILE
from src.pet_animations import draw_mood, draw_speech_bubble, clear_speech_bubble, CANVAS_SIZE

POLL_INTERVAL_MS = 4000       # check pet_state.json every 4 seconds
ANIMATION_INTERVAL_MS = 33    # ~30fps idle animation
BUBBLE_DURATION_MS = 9000     # speech bubble stays up ~9 seconds


class PetWidget:
    def __init__(self, root):
        self.root = root
        self.tick = 0
        self.last_seen_updated_at = None
        self.current_mood = "idle"
        self.current_tone = "neutral"
        self.bubble_active = False
        self.bubble_hide_job = None

        self._setup_window()
        self._setup_canvas()

        self._animation_loop()
        self._poll_loop()

    def _setup_window(self):
        self.root.overrideredirect(True)   # no title bar/borders
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{CANVAS_SIZE}x{CANVAS_SIZE}+100+100")
        self.root.attributes("-transparentcolor", "white")
        # Right-click to close, since there's no title bar close button
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

    def _setup_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg="white", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

    def _animation_loop(self):
        draw_mood(self.canvas, self.current_mood, self.tick, self.current_tone)
        if self.bubble_active:
            # bubble text is redrawn by _show_bubble via tags, no need to
            # redraw here every tick - draw_mood already clears/redraws
            # only the "pet" tag, leaving "bubble" tag intact
            pass
        self.tick += 1
        self.root.after(ANIMATION_INTERVAL_MS, self._animation_loop)

    def _poll_loop(self):
        self._check_pet_state()
        self.root.after(POLL_INTERVAL_MS, self._poll_loop)

    def _check_pet_state(self):
        if not os.path.exists(PET_STATE_FILE):
            return  # roast.py hasn't run yet; stay in default idle state

        try:
            with open(PET_STATE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return  # file mid-write or corrupted; skip this poll, try again next cycle

        updated_at = data.get("updated_at")
        self.current_mood = data.get("mood", "idle")
        self.current_tone = data.get("tone_bucket", "neutral")

        if updated_at and updated_at != self.last_seen_updated_at:
            self.last_seen_updated_at = updated_at
            roast_text = data.get("latest_roast", "")
            self._show_bubble(roast_text)

    def _show_bubble(self, text):
        draw_speech_bubble(self.canvas, text)
        self.bubble_active = True

        if self.bubble_hide_job is not None:
            self.root.after_cancel(self.bubble_hide_job)
        self.bubble_hide_job = self.root.after(BUBBLE_DURATION_MS, self._hide_bubble)

    def _hide_bubble(self):
        clear_speech_bubble(self.canvas)
        self.bubble_active = False
        self.bubble_hide_job = None

    def _on_click(self, event):
        # Stage 4 will implement the history panel here.
        # Left as a no-op placeholder for now so clicking doesn't error.
        pass


def main():
    root = tk.Tk()
    PetWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()