#!/usr/bin/env python3
"""
test_pets.py - Auto-discovering live preview of ALL pets in src/pets/.

Add a new pet file (e.g. src/pets/alien.py) with draw_idle/happy/angry/sick
and it shows up here instantly. No edits to this file needed.
"""
import tkinter as tk
import sys
import os
import importlib
import pkgutil
import inspect

# Repo root on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import src.pets  # triggers __init__.py

MOODS = ["idle", "happy", "angry", "sick"]
TONE = "#4A3A2A"
REQUIRED_FUNCS = {f"draw_{m}" for m in MOODS}


def discover_pets():
    """Dynamically import every pet module that has all 4 draw functions."""
    pets = {}
    for _, modname, ispkg in pkgutil.iter_modules(src.pets.__path__):
        if ispkg:
            continue
        try:
            mod = importlib.import_module(f"src.pets.{modname}")
        except Exception as e:
            print(f"Skipping {modname}: {e}")
            continue

        if all(hasattr(mod, fn) for fn in REQUIRED_FUNCS):
            # Use title-cased filename as display name
            pets[modname.title()] = mod
        else:
            print(f"Skipping {modname}: missing required draw_* functions")
    return pets


class PetPreview:
    def __init__(self, parent, name, module):
        self.name = name
        self.module = module
        self.tick = 0
        self.mood = "idle"

        self.frame = tk.Frame(parent, bg="#1a1a1a", padx=12, pady=10)
        self.frame.pack(side=tk.LEFT, fill="both", expand=True)

        tk.Label(
            self.frame, text=name, font=("Segoe UI", 13, "bold"),
            fg="white", bg="#1a1a1a"
        ).pack(pady=(0, 4))

        self.canvas = tk.Canvas(
            self.frame, width=220, height=220,
            bg="#1a1a1a", highlightthickness=1, highlightbackground="#444"
        )
        self.canvas.pack()

        btn_frame = tk.Frame(self.frame, bg="#1a1a1a")
        btn_frame.pack(pady=8)
        for mood in MOODS:
            btn = tk.Button(
                btn_frame, text=mood.capitalize(), width=7,
                command=lambda m=mood: self.set_mood(m)
            )
            btn.pack(side=tk.LEFT, padx=2)

        self.animate()

    def set_mood(self, mood):
        self.mood = mood

    def animate(self):
        self.tick += 1
        draw_fn = getattr(self.module, f"draw_{self.mood}", self.module.draw_idle)
        draw_fn(self.canvas, self.tick, TONE)
        self.frame.after(33, self.animate)


def main():
    pets = discover_pets()
    if not pets:
        print("No valid pets found in src/pets/. Each pet needs draw_idle, draw_happy, draw_angry, draw_sick.")
        return

    root = tk.Tk()
    root.title(f"RoastBot Pet Tester — {len(pets)} pets found")
    root.configure(bg="#1a1a1a")

    tk.Label(
        root, text="Pet Face Tester (Auto-Discover)",
        font=("Segoe UI", 16, "bold"), fg="#FFD95A", bg="#1a1a1a"
    ).pack(pady=8)

    # Grid rows: 2 pets per row
    pet_names = list(pets.keys())
    container = tk.Frame(root, bg="#1a1a1a")
    container.pack(padx=10, pady=5)

    for i in range(0, len(pet_names), 2):
        row = tk.Frame(container, bg="#1a1a1a")
        row.pack(pady=8)
        PetPreview(row, pet_names[i], pets[pet_names[i]])
        if i + 1 < len(pet_names):
            PetPreview(row, pet_names[i + 1], pets[pet_names[i + 1]])

    tk.Label(
        root,
        text="Add a new .py to src/pets/ with draw_idle/happy/angry/sick → rerun to see it",
        font=("Segoe UI", 9), fg="#777", bg="#1a1a1a"
    ).pack(pady=8)

    root.mainloop()


if __name__ == "__main__":
    main()