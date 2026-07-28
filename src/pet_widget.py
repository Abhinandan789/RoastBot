"""
pet_widget.py - Floating desktop pet with animated speech bubble + TTS.

Pet design is loaded via the existing registry (src/pets/registry.py),
driven by ACTIVE_PET in .env - unchanged from v2.2.0/v3.0.0. This stage
only adds bubble animation (entrance bounce, typing effect, exit shrink)
and voice playback on top of that existing architecture.
"""

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import json
import os
import tkinter as tk

from src.config import PET_STATE_FILE, ACTIVE_PET
from src.pets.registry import get_active_pet_module
from src.pet_animations import (
    draw_mood, compute_bubble_geometry, render_bubble,
    CANVAS_SIZE, TRANSPARENT_KEY
)
from src.db import get_recent_roasts
from src.sounds import play_typing_click
from src.tts import speak

POLL_INTERVAL_MS = 4000
ANIMATION_INTERVAL_MS = 33
BUBBLE_DURATION_MS = 12000
TYPING_SPEED_MS = 28
CURSOR_BLINK_MS = 530

_active_pet_module = get_active_pet_module(ACTIVE_PET)


class BubbleWindow:
    """
    Animated speech bubble: entrance bounce, character-by-character
    typing with click sound, blinking cursor once typing completes,
    voice playback after typing finishes, and an exit shrink animation.
    """

    _BOUNCE_OFFSETS = [28, 20, 12, 5, 0, -3, -1, 0]

    def __init__(self, parent_root, pet_widget):
        self.parent = parent_root
        self.pet_widget = pet_widget
        self.toplevel = None
        self.canvas = None
        self._jobs = []
        self.full_text = ""
        self.typed_text = ""
        self.mood = "idle"
        self.bw = self.bh = self.ww = self.wh = 0
        self.final_x = self.final_y = 0

    def _cancel_jobs(self):
        for job in self._jobs:
            self.parent.after_cancel(job)
        self._jobs.clear()

    def _ensure_window(self, width, height):
        if self.toplevel is None:
            self.toplevel = tk.Toplevel(self.parent)
            self.toplevel.overrideredirect(True)
            self.toplevel.attributes("-topmost", True)
            try:
                self.toplevel.attributes("-transparentcolor", TRANSPARENT_KEY)
            except tk.TclError:
                pass
            self.canvas = tk.Canvas(
                self.toplevel, width=width, height=height,
                bg=TRANSPARENT_KEY, highlightthickness=0
            )
            self.canvas.pack()
        else:
            self.canvas.config(width=width, height=height)
        self.toplevel.geometry(f"{width}x{height}")

    def show(self, text, mood="idle"):
        self._cancel_jobs()
        self.full_text = text
        self.mood = mood
        self.typed_text = ""

        wrapped, bw, bh, ww, wh = compute_bubble_geometry(text)
        self.bw, self.bh, self.ww, self.wh = bw, bh, ww, wh

        px = self.pet_widget.root.winfo_x()
        py = self.pet_widget.root.winfo_y()
        pw = self.pet_widget.root.winfo_width()

        self.final_x = px + (pw - ww) // 2
        self.final_y = py - wh + 30

        self._ensure_window(ww, wh)
        start_y = self.final_y + self._BOUNCE_OFFSETS[0]
        self.toplevel.geometry(f"{ww}x{wh}+{self.final_x}+{start_y}")
        self.toplevel.deiconify()

        self._animate_entrance(0)

    def hide(self):
        self._cancel_jobs()
        self._animate_exit(0)

    def _animate_entrance(self, frame):
        if frame >= len(self._BOUNCE_OFFSETS):
            self._start_typing()
            return
        y = self.final_y + self._BOUNCE_OFFSETS[frame]
        self.toplevel.geometry(f"{self.ww}x{self.wh}+{self.final_x}+{y}")
        render_bubble(self.canvas, "", self.bw, self.bh, self.mood, False)
        job = self.parent.after(30, lambda: self._animate_entrance(frame + 1))
        self._jobs.append(job)

    def _start_typing(self):
        self._type_next(0)

    def _type_next(self, index):
        if index > len(self.full_text):
            self._start_cursor_blink()
            speak(self.full_text, ACTIVE_PET)
            return
        self.typed_text = self.full_text[:index]
        render_bubble(self.canvas, self.typed_text, self.bw, self.bh, self.mood, True)
        play_typing_click()
        job = self.parent.after(TYPING_SPEED_MS, lambda: self._type_next(index + 1))
        self._jobs.append(job)

    def _start_cursor_blink(self):
        cursor_state = {"on": False}

        def blink():
            if not self.toplevel or not self.toplevel.winfo_exists():
                return
            cursor_state["on"] = not cursor_state["on"]
            render_bubble(self.canvas, self.typed_text, self.bw, self.bh, self.mood, cursor_state["on"])
            job = self.parent.after(CURSOR_BLINK_MS, blink)
            self._jobs.append(job)

        blink()

    def _animate_exit(self, frame):
        if frame >= 8:
            if self.toplevel:
                self.toplevel.withdraw()
            return
        t = frame / 8
        y = self.final_y + int(t * 20)
        w = max(1, int(self.ww * (1.0 - t * 0.25)))
        h = max(1, int(self.wh * (1.0 - t * 0.25)))
        x = self.final_x + (self.ww - w) // 2
        self.toplevel.geometry(f"{w}x{h}+{x}+{y}")
        self.canvas.config(width=w, height=h)
        job = self.parent.after(20, lambda: self._animate_exit(frame + 1))
        self._jobs.append(job)

    def destroy(self):
        self._cancel_jobs()
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
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_moved = False
        self._history_panel = None

        self.bubble = BubbleWindow(self.root, self)

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
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

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
        self.bubble.show(text, mood=self.current_mood)
        if self.bubble_hide_job is not None:
            self.root.after_cancel(self.bubble_hide_job)
        self.bubble_hide_job = self.root.after(BUBBLE_DURATION_MS, self._hide_bubble)

    def _hide_bubble(self):
        self.bubble.hide()
        self.bubble_hide_job = None

    def _on_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._drag_moved = False

    def _on_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._drag_moved = True
        new_x = self.root.winfo_x() + dx
        new_y = self.root.winfo_y() + dy
        self.root.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event):
        if not self._drag_moved:
            self._open_history_panel()

    def _on_close(self):
        self.bubble.destroy()
        self.root.destroy()

    def _open_history_panel(self):
        if self._history_panel is not None and self._history_panel.winfo_exists():
            self._history_panel.lift()
            self._history_panel.focus_force()
            return

        panel = tk.Toplevel(self.root)
        panel.title("Roast History")
        panel.geometry("340x420")
        panel.attributes("-topmost", True)
        panel.protocol("WM_DELETE_WINDOW", lambda: self._close_history_panel(panel))

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
        text_widget.config(state="disabled")

        tk.Button(panel, text="Close", command=lambda: self._close_history_panel(panel)).pack(pady=6)
        self._history_panel = panel

    def _close_history_panel(self, panel):
        panel.destroy()
        self._history_panel = None


def main():
    root = tk.Tk()
    PetWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()