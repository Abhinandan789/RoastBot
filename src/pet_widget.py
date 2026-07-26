"""
pet_widget.py - The floating desktop pet window.

Single responsibility: manage the Tkinter window lifecycle, run the
continuous animation loop, poll pet_state.json for changes, trigger the
auto-popup speech bubble (hosted in its own Toplevel via BubbleWindow) when
a new roast arrives, and show a history panel on click. Pet drawing and
bubble geometry are delegated entirely to pet_animations.py.

This process is independent from roast.py - it only reads pet_state.json,
never writes to it, and never calls the GitHub/Groq APIs directly.
"""

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  # not on Windows, or older Windows version without this API

import json
import os
import tkinter as tk

from src.config import PET_STATE_FILE
from src.pet_animations import (
    draw_mood, compute_bubble_geometry, render_bubble,
    CANVAS_SIZE, TRANSPARENT_KEY
)
from src.db import get_recent_roasts

POLL_INTERVAL_MS = 4000
ANIMATION_INTERVAL_MS = 33
BUBBLE_DURATION_MS = 12000


class BubbleWindow:
    """
    Manages an independent, borderless Toplevel window that floats above
    the pet, sized dynamically to fit whatever text it's showing. Kept
    separate from PetWidget's main canvas so bubble sizing/styling never
    fights with the fixed-size pet canvas.
    """

    def __init__(self, parent_root):
        self.parent_root = parent_root
        self.toplevel = None
        self.canvas = None

    def show(self, text):
        wrapped, bw, bh, ww, wh = compute_bubble_geometry(text)
        self._ensure_window(ww, wh)
        render_bubble(self.canvas, wrapped, bw, bh)
        self._position(ww, wh)
        self.toplevel.deiconify()

    def _ensure_window(self, width, height):
        if self.toplevel is None:
            self.toplevel = tk.Toplevel(self.parent_root)
            self.toplevel.overrideredirect(True)
            self.toplevel.attributes("-topmost", True)
            try:
                self.toplevel.attributes("-transparentcolor", TRANSPARENT_KEY)
            except tk.TclError:
                pass  # not supported on this platform - falls back to opaque
            self.canvas = tk.Canvas(
                self.toplevel, width=width, height=height,
                bg=TRANSPARENT_KEY, highlightthickness=0
            )
            self.canvas.pack()
        else:
            self.canvas.config(width=width, height=height)
        self.toplevel.geometry(f"{width}x{height}")

    def _position(self, width, height):
        self.parent_root.update_idletasks()
        px = self.parent_root.winfo_x()
        py = self.parent_root.winfo_y()
        pw = self.parent_root.winfo_width()
        x = px + (pw - width) // 2
        y = py - height + 15
        self.toplevel.geometry(f"{width}x{height}+{x}+{y}")

    def hide(self):
        if self.toplevel is not None:
            self.toplevel.withdraw()

    def destroy(self):
        if self.toplevel is not None:
            self.toplevel.destroy()
            self.toplevel = None
            self.canvas = None


class PetWidget:
    def __init__(self, root):
        self.root = root
        self.tick = 0
        self.last_seen_updated_at = None
        self.current_mood = "idle"
        self.current_tone = "neutral"
        self.bubble_hide_job = None

        self.bubble = BubbleWindow(self.root)

        self._setup_window()
        self._setup_canvas()

        self._animation_loop()
        self._poll_loop()

    def _setup_window(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{CANVAS_SIZE}x{CANVAS_SIZE}+100+200")
        try:
            self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass
        self.root.bind("<Button-3>", lambda e: self._on_close())

    def _setup_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg=TRANSPARENT_KEY, highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)

    def _animation_loop(self):
        draw_mood(self.canvas, self.current_mood, self.tick, self.current_tone)
        self.tick += 1
        self.root.after(ANIMATION_INTERVAL_MS, self._animation_loop)

    def _poll_loop(self):
        self._check_pet_state()
        self.root.after(POLL_INTERVAL_MS, self._poll_loop)

    def _check_pet_state(self):
        if not os.path.exists(PET_STATE_FILE):
            return

        try:
            with open(PET_STATE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        updated_at = data.get("updated_at")
        self.current_mood = data.get("mood", "idle")
        self.current_tone = data.get("tone_bucket", "neutral")

        if updated_at and updated_at != self.last_seen_updated_at:
            self.last_seen_updated_at = updated_at
            roast_text = data.get("latest_roast", "")
            self._show_bubble(roast_text)

    def _show_bubble(self, text):
        self.bubble.show(text)
        if self.bubble_hide_job is not None:
            self.root.after_cancel(self.bubble_hide_job)
        self.bubble_hide_job = self.root.after(BUBBLE_DURATION_MS, self._hide_bubble)

    def _hide_bubble(self):
        self.bubble.hide()
        self.bubble_hide_job = None

    def _on_click(self, event):
        self._open_history_panel()

    def _on_close(self):
        self.bubble.destroy()
        self.root.destroy()

    def _open_history_panel(self):
        panel = tk.Toplevel(self.root)
        panel.title("Roast History")
        panel.geometry("340x420")
        panel.attributes("-topmost", True)

        frame = tk.Frame(panel)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            frame, wrap="word", yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9), state="normal", padx=8, pady=8
        )
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        recent = get_recent_roasts(limit=10)
        if not recent:
            text_widget.insert("end", "No roast history yet.")
        else:
            for i, roast_text in enumerate(recent, start=1):
                text_widget.insert("end", f"{i}. {roast_text}\n\n")

        text_widget.config(state="disabled")  # read-only after populating

        close_btn = tk.Button(panel, text="Close", command=panel.destroy)
        close_btn.pack(pady=6)


def main():
    root = tk.Tk()
    PetWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()