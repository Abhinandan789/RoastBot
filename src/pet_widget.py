"""
pet_widget.py - Floating desktop pet with animated speech bubble + TTS.
"""

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import json
import os
import time
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
from src.scheduler import start_background_scheduler

POLL_INTERVAL_MS = 4000
ANIMATION_INTERVAL_MS = 33
TYPING_SPEED_MS = 28
CURSOR_BLINK_MS = 530
BUBBLE_STAY_AFTER_TYPING_MS = 5000
BUBBLE_MAX_LIFETIME_MS = 20000

_active_pet_module = get_active_pet_module(ACTIVE_PET)


class BubbleWindow:
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
        self._tts_started = False

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

    def _calc_position(self, ww, wh):
        self.pet_widget.root.update_idletasks()
        px = self.pet_widget.root.winfo_x()
        py = self.pet_widget.root.winfo_y()
        pw = self.pet_widget.root.winfo_width()

        x = px + (pw - ww) // 2
        y = py - wh + 35

        sw = self.pet_widget.root.winfo_screenwidth()
        sh = self.pet_widget.root.winfo_screenheight()
        x = max(10, min(x, sw - ww - 10))
        y = max(10, min(y, sh - wh - 10))
        return x, y

    def _move_to(self, x, y, w=None, h=None):
        w = w or self.ww
        h = h or self.wh
        self.toplevel.geometry(f"{w}x{h}+{x}+{y}")

    def show(self, text, mood="idle"):
        # === DEDUP: don't restart if same text is already showing ===
        if (self.toplevel is not None
                and self.toplevel.winfo_viewable()
                and self.full_text == text):
            return
        self._cancel_jobs()
        self.full_text = text
        self.mood = mood
        self.typed_text = ""
        self._tts_started = False

        wrapped, bw, bh, ww, wh = compute_bubble_geometry(text)
        self.bw, self.bh, self.ww, self.wh = bw, bh, ww, wh

        self.final_x, self.final_y = self._calc_position(ww, wh)

        self._ensure_window(ww, wh)
        start_y = self.final_y + self._BOUNCE_OFFSETS[0]
        self._move_to(self.final_x, start_y)
        self.toplevel.deiconify()

        job = self.parent.after(BUBBLE_MAX_LIFETIME_MS, self.hide)
        self._jobs.append(job)

        self._animate_entrance(0)

    def sync_position(self):
        if self.toplevel is None or not self.toplevel.winfo_viewable():
            return
        self.final_x, self.final_y = self._calc_position(self.ww, self.wh)
        self._move_to(self.final_x, self.final_y)

    def hide(self):
        if self.toplevel is None:
            return
        self._cancel_jobs()
        self._animate_exit(0)

    def _animate_entrance(self, frame):
        if frame >= len(self._BOUNCE_OFFSETS):
            self._start_typing()
            return
        y = self.final_y + self._BOUNCE_OFFSETS[frame]
        self._move_to(self.final_x, y)
        render_bubble(self.canvas, "", self.bw, self.bh, self.mood, False)
        job = self.parent.after(30, lambda: self._animate_entrance(frame + 1))
        self._jobs.append(job)

    def _start_typing(self):
        if not self._tts_started and self.toplevel and self.toplevel.winfo_exists():
            self._tts_started = True
            speak(self.full_text, ACTIVE_PET)
        self._type_next(0)

    def _type_next(self, index):
        if index > len(self.full_text):
            self._start_cursor_blink()
            job = self.parent.after(BUBBLE_STAY_AFTER_TYPING_MS, self.hide)
            self._jobs.append(job)
            return

        self.typed_text = self.full_text[:index]
        render_bubble(self.canvas, self.typed_text, self.bw, self.bh,
                      self.mood, True)
        play_typing_click()
        job = self.parent.after(TYPING_SPEED_MS,
                                lambda: self._type_next(index + 1))
        self._jobs.append(job)

    def _start_cursor_blink(self):
        state = {"on": False}

        def blink():
            if not self.toplevel or not self.toplevel.winfo_exists():
                return
            state["on"] = not state["on"]
            render_bubble(self.canvas, self.typed_text, self.bw, self.bh,
                          self.mood, state["on"])
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
        self._move_to(x, y, w, h)
        job = self.parent.after(20, lambda: self._animate_exit(frame + 1))
        self._jobs.append(job)

    def destroy(self):
        self._cancel_jobs()
        if self.toplevel is not None:
            self.toplevel.destroy()
            self.toplevel = None
            self.canvas = None

    def _prime_pet_state(self):
        """
        Snapshot whatever pet_state.json already exists on disk at launch
        as 'already seen', without popping a bubble for it. Without this,
        the stale roast from your last session gets replayed as a bubble
        immediately on startup, right before the freshly-triggered
        scheduler run finishes and writes a second, near-identical
        update - which is why the same roast + speech fired twice back
        to back on every launch.
        """
        if not os.path.exists(PET_STATE_FILE):
            return
        try:
            with open(PET_STATE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        self.last_seen_updated_at = data.get("updated_at")
        self.current_mood = data.get("mood", "idle")
        self.current_tone = data.get("tone_bucket", "neutral")


class PetWidget:
    def __init__(self, root):
        self.root = root
        self.tick = 0
        self.last_seen_updated_at = None
        self.current_mood = "idle"
        self.current_tone = "neutral"
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_moved = False
        self._history_panel = None
        self._last_shown_roast = None
        self._last_shown_time = 0

        self.bubble = BubbleWindow(self.root, self)

        self._setup_window()
        self._setup_canvas()

        self._prime_pet_state()
        start_background_scheduler()

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

    def _prime_pet_state(self):
        # ""Snapshot whatever pet_state.json already exists on disk at launch
        # as 'already seen', without popping a bubble for it. Without this,
        # the stale roast from your last session gets replayed as a bubble
        # immediately on startup, right before the freshly-triggered
        # scheduler run finishes and writes a second, near-identical
        # update - which is why the same roast + speech fired twice back
        # to back on every launch.
        if not os.path.exists(PET_STATE_FILE):
            return
        try:
            with open(PET_STATE_FILE) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return
        self.last_seen_updated_at = data.get("updated_at")
        self.current_mood = data.get("mood", "idle")
        self.current_tone = data.get("tone_bucket", "neutral")

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
            roast_text = data.get("latest_roast", "")
            self.last_seen_updated_at = updated_at

            # Deduplicate: same roast text within 30s = don't re-show
            now = time.time()
            if self._last_shown_roast == roast_text and now - self._last_shown_time < 30:
                return

            self._last_shown_roast = roast_text
            self._last_shown_time = now
            self._show_bubble(roast_text)

    def _show_bubble(self, text):
        self.bubble.hide()
        self.bubble.show(text, mood=self.current_mood)

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
        self.bubble.sync_position()

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

        tk.Button(panel, text="Close",
                  command=lambda: self._close_history_panel(panel)).pack(pady=6)
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