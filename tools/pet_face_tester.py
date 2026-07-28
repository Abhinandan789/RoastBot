#!/usr/bin/env python3
"""
tools/pet_face_tester.py - Modern dark-themed pet preview grid.
Responsive: works windowed or fullscreen without breaking layout.
"""
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pets.registry import PET_REGISTRY, get_active_pet_module
from src.pet_animations import compute_bubble_geometry, render_bubble
from src.sounds import play_typing_click
from src.tts import speak

MOODS = ["idle", "happy", "angry", "sick"]
TONE = "#4A3A2A"

SAMPLE_ROASTS = {
    "idle":  "Ain't nothin' poppin' with you, just a whole lotta nothin'.",
    "happy": "Yo, actual commits? Didn't know you had it in you. Proud-ish.",
    "angry": "You ghosted for a whole day. My respect is evaporating.",
    "sick":  "Three days of silence. You alive or did your IDE finally win?",
}

VOICE_SAMPLES = {
    "droplet": "Hey! I'm Droplet. Quick, bubbly, and here to hydrate your ego.",
    "smiley":  "Hi there! I'm Smiley. I'll cheer you on... until you disappoint me.",
    "ghost":   "Boo. I'm Ghost. I float around and watch you ignore your goals.",
    "robot":   "Beep boop. I'm Robot. Efficiency is my religion. You are... not efficient.",
    "cat":     "Meow. I'm the cat. I judge your commits silently. Harshly.",
}


# ------------------------------------------------------------------
#  Flat button with rounded corners + hover
# ------------------------------------------------------------------
class FlatButton(tk.Canvas):
    def __init__(self, parent, text, width=80, height=28, bg="#333", fg="white",
                 hover_bg="#444", active_bg="#555", command=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self._text = text
        self._bg = bg
        self._fg = fg
        self._hover = hover_bg
        self._active = active_bg
        self._cmd = command

        self._rect = self._rounded_rect(2, 2, width-2, height-2, 6, fill=bg, outline="")
        self._txt = self.create_text(width//2, height//2, text=text,
                                     fill=fg, font=("Segoe UI", 9, "bold"))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
                  x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def _on_enter(self, _):
        self.itemconfig(self._rect, fill=self._hover)

    def _on_leave(self, _):
        self.itemconfig(self._rect, fill=self._bg)

    def _on_press(self, _):
        self.itemconfig(self._rect, fill=self._active)

    def _on_release(self, _):
        self.itemconfig(self._rect, fill=self._hover)
        if self._cmd:
            self._cmd()


# ------------------------------------------------------------------
#  Mood pill button
# ------------------------------------------------------------------
class MoodButton(tk.Canvas):
    COLORS = {
        "idle":  ("#4A4A4A", "#666666"),
        "happy": ("#2A5A3A", "#44AA66"),
        "angry": ("#5A2A2A", "#AA4444"),
        "sick":  ("#3A5A3A", "#66AA66"),
    }

    def __init__(self, parent, mood, command=None):
        self.mood = mood
        base, _ = self.COLORS[mood]
        super().__init__(parent, width=56, height=26, bg=parent["bg"],
                         highlightthickness=0, cursor="hand2")
        self._cmd = command
        self._rect = self._rounded_rect(1, 1, 55, 25, 12, fill=base, outline="")
        self._txt = self.create_text(28, 13, text=mood.capitalize(),
                                     fill="#DDD", font=("Segoe UI", 8, "bold"))
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<Button-1>", lambda e: self._cmd() if self._cmd else None)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
                  x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def _hover(self, active):
        _, accent = self.COLORS[self.mood]
        self.itemconfig(self._rect, fill=accent if active else self.COLORS[self.mood][0])
        self.itemconfig(self._txt, fill="white" if active else "#DDD")


# ------------------------------------------------------------------
#  Pet Card
# ------------------------------------------------------------------
class PetCard(tk.Frame):
    def __init__(self, parent, name, pet_key):
        super().__init__(parent, bg="#1E1E1E", padx=16, pady=16)

        self.name = name
        self.pet_key = pet_key
        self.module = get_active_pet_module(pet_key)
        self.tick = 0
        self.mood = "idle"
        self._popup = None
        self._jobs = []

        self.config(highlightbackground="#2A2A2A", highlightthickness=1)

        # Title
        tk.Label(self, text=name, font=("Segoe UI", 14, "bold"),
                 fg="#F0F0F0", bg="#1E1E1E").pack(pady=(0, 10))

        # Canvas frame
        canvas_frame = tk.Frame(self, bg="#252525", padx=3, pady=3)
        canvas_frame.pack()
        self.canvas = tk.Canvas(
            canvas_frame, width=180, height=180,
            bg="#1a1a1a", highlightthickness=0
        )
        self.canvas.pack()

        # Mood pills
        mood_frame = tk.Frame(self, bg="#1E1E1E")
        mood_frame.pack(pady=12)
        for mood in MOODS:
            MoodButton(mood_frame, mood,
                       command=lambda m=mood: self.set_mood(m)).pack(side=tk.LEFT, padx=3)

        # Action buttons
        btn_frame = tk.Frame(self, bg="#1E1E1E")
        btn_frame.pack(pady=(2, 0))

        FlatButton(btn_frame, "Test Roast", width=90, height=30,
                   bg="#2D2D2D", hover_bg="#3D3D3D", active_bg="#4D4D4D",
                   command=self._test_roast).pack(side=tk.LEFT, padx=4)

        FlatButton(btn_frame, "Voice", width=64, height=30,
                   bg="#1A3A4A", fg="#7EC8E3", hover_bg="#224A5E", active_bg="#2A5A70",
                   command=self._voice_sample).pack(side=tk.LEFT, padx=4)

        self.animate()

    def set_mood(self, mood):
        self.mood = mood

    def _cancel_jobs(self):
        for job in self._jobs:
            self.after_cancel(job)
        self._jobs.clear()

    def _voice_sample(self):
        sample = VOICE_SAMPLES.get(
            self.pet_key,
            f"Hi, I'm {self.name}. I exist to judge your productivity."
        )
        speak(sample, self.pet_key)

    def _test_roast(self):
        self._cancel_jobs()
        if self._popup is not None:
            try:
                self._popup.destroy()
            except tk.TclError:
                pass

        text = SAMPLE_ROASTS.get(self.mood, SAMPLE_ROASTS["idle"])
        wrapped, bw, bh, ww, wh = compute_bubble_geometry(text)

        self._popup = tk.Toplevel(self)
        self._popup.overrideredirect(True)
        self._popup.attributes("-topmost", True)
        try:
            self._popup.attributes("-transparentcolor", "#FE01FE")
        except tk.TclError:
            pass

        self.update_idletasks()
        cx = self.winfo_rootx() + self.winfo_width() // 2
        cy = self.winfo_rooty() + 40

        self._popup.geometry(f"{ww}x{wh}+{cx - ww // 2}+{cy - wh + 30}")

        c = tk.Canvas(self._popup, width=ww, height=wh,
                      bg="#FE01FE", highlightthickness=0)
        c.pack()

        offsets = [28, 20, 12, 5, 0, -3, -1, 0]
        idx = [0]

        def bounce():
            if idx[0] < len(offsets):
                y = cy - wh + 30 + offsets[idx[0]]
                self._popup.geometry(f"{ww}x{wh}+{cx - ww // 2}+{y}")
                render_bubble(c, "", bw, bh, self.mood, False)
                idx[0] += 1
                self._popup.after(30, bounce)
            else:
                type_char(0, text, c, bw, bh)

        def type_char(i, full, canvas, bw, bh):
            if i > len(full):
                speak(full, self.pet_key)
                self._popup.after(5000, lambda: self._safe_destroy())
                return
            render_bubble(canvas, full[:i], bw, bh, self.mood, True)
            play_typing_click()
            self._popup.after(30, lambda: type_char(i + 1, full, canvas, bw, bh))

        bounce()

    def _safe_destroy(self):
        if self._popup is not None:
            try:
                self._popup.destroy()
            except tk.TclError:
                pass
            self._popup = None

    def animate(self):
        self.tick += 1
        self.canvas.delete("pet")
        draw_fn = getattr(self.module, f"draw_{self.mood}", self.module.draw_idle)
        draw_fn(self.canvas, self.tick, TONE)
        self.after(33, self.animate)


# ------------------------------------------------------------------
#  Main App
# ------------------------------------------------------------------
def main():
    if not PET_REGISTRY:
        print("No pets registered in src/pets/registry.py")
        return

    root = tk.Tk()
    root.title("RoastBot Pet Tester")
    root.configure(bg="#121212")
    root.geometry("1100x800")
    root.minsize(800, 600)

    # Header
    header = tk.Frame(root, bg="#121212", pady=18)
    header.pack(fill="x")
    tk.Label(header, text="RoastBot", font=("Segoe UI", 26, "bold"),
             fg="#FFD95A", bg="#121212").pack()
    tk.Label(header, text="Pet Design & Voice Preview",
             font=("Segoe UI", 11), fg="#888", bg="#121212").pack(pady=(4, 0))

    legend = tk.Frame(root, bg="#121212", pady=6)
    legend.pack()
    tk.Label(legend, text="Mood = face  ·  Test Roast = bubble + typing + voice  ·  Voice = instant preview",
             font=("Segoe UI", 9), fg="#555", bg="#121212").pack()

    # ---- Scrollable canvas ----
    main_canvas = tk.Canvas(root, bg="#121212", highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview,
                             bg="#1E1E1E", troughcolor="#121212")
    scrollable_frame = tk.Frame(main_canvas, bg="#121212")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )

    # Create the inner window — width will be updated dynamically on resize
    inner_window = main_canvas.create_window((0, 0), window=scrollable_frame,
                                             anchor="nw", width=1060)
    main_canvas.configure(yscrollcommand=scrollbar.set)

    main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ---- Centered grid container ----
    # Wrap the grid in a frame that fills width and centers its contents
    outer_container = tk.Frame(scrollable_frame, bg="#121212")
    outer_container.pack(fill="x", expand=True, pady=10)

    # Centering helper: a frame that stays centered regardless of parent width
    center_wrapper = tk.Frame(outer_container, bg="#121212")
    center_wrapper.pack(expand=True)  # expand=True centers it horizontally

    names = list(PET_REGISTRY.keys())
    COLS = 3
    for i, key in enumerate(names):
        row = i // COLS
        col = i % COLS
        card = PetCard(center_wrapper, key.title(), key)
        card.grid(row=row, column=col, padx=14, pady=14, sticky="n")

    # Footer
    tk.Label(scrollable_frame,
             text="Add a new pet to PET_REGISTRY in src/pets/registry.py → rerun to see it",
             font=("Segoe UI", 9), fg="#444", bg="#121212").pack(pady=16)

    # ---- Responsive: update inner canvas width on resize ----
    def _on_resize(event):
        # Update the inner window width to match canvas width minus padding
        new_width = max(400, event.width - 40)
        main_canvas.itemconfig(inner_window, width=new_width)

    main_canvas.bind("<Configure>", _on_resize)

    root.mainloop()


if __name__ == "__main__":
    main()