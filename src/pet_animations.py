"""
pet_animations.py - Pure drawing logic for the desktop pet.

Single responsibility: given a Tkinter canvas, a mood, a tone bucket, and
a "tick" (an incrementing frame counter), draw the correct pose. No window
management, no polling, no file access happens here - this file only
knows how to draw, nothing about when or why.

Speech bubble drawing is canvas-agnostic: compute_bubble_geometry() figures
out sizing from the text, render_bubble() draws onto whatever canvas it's
given (starting at 0,0) - this lets pet_widget.py host the bubble in its
own dedicated Toplevel window, independent from the pet's canvas.

Swappable later: if real sprite art replaces the procedural pet shapes,
only the mood-drawing section of this file changes.
"""

import math
import textwrap
import tkinter as tk

CANVAS_SIZE = 280
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2
BASE_RADIUS = 42

TRANSPARENT_KEY = "#FE01FE"  # unlikely-to-clash magenta, used only as the
                              # widget's transparent background key - never
                              # use this exact color for any drawn fill

TONE_COLORS = {
    "warm": "#FFD700",
    "neutral": "#6E6E6E",
    "cynical": "#5C6B73",
    "checked_out": "#3A3A3A"
}

MOOD_FILL_COLORS = {
    "happy": "#FFE4B5",
    "angry": "#FF6B6B",
    "sick": "#A8C0A0",
    "idle": "#E8D8C0"
}


def get_tone_color(tone_bucket):
    return TONE_COLORS.get(tone_bucket, TONE_COLORS["neutral"])

from src.pets.registry import get_active_pet_module
from src.config import ACTIVE_PET

_active_module = get_active_pet_module(ACTIVE_PET)

CANVAS_SIZE = getattr(_active_module, "CANVAS_SIZE", 220)


def draw_mood(canvas, mood, tick, tone_bucket="neutral"):
    tone_color = get_tone_color(tone_bucket)
    draw_fn = {
        "happy": _active_module.draw_happy,
        "angry": _active_module.draw_angry,
        "sick": _active_module.draw_sick,
        "idle": _active_module.draw_idle,
    }.get(mood, _active_module.draw_idle)
    draw_fn(canvas, tick, tone_color)


# ---------------------------------------------------------------------
# Universal eye tracker - any pet can call this
# ---------------------------------------------------------------------

def track_mouse(canvas, eye_cx, eye_cy, pupil_radius=3, max_offset=4):
    """
    Returns (pupil_x, pupil_y) clamped inside the eye so it follows
    the mouse cursor. Call this inside your draw loop.
    """
    try:
        mx = canvas.winfo_pointerx() - canvas.winfo_rootx()
        my = canvas.winfo_pointery() - canvas.winfo_rooty()
    except tk.TclError:
        return eye_cx, eye_cy

    dx = mx - eye_cx
    dy = my - eye_cy
    dist = math.hypot(dx, dy)
    if dist == 0:
        return eye_cx, eye_cy

    # Clamp pupil inside eye
    offset = min(max_offset, dist / 8)
    angle = math.atan2(dy, dx)
    return eye_cx + math.cos(angle) * offset, eye_cy + math.sin(angle) * offset


# ---------------------------------------------------------------------
# Speech bubble — canvas-agnostic, hosted in its own Toplevel by
# pet_widget.py. Everything below draws starting at (0,0).
# ---------------------------------------------------------------------

BUBBLE_PADDING = 16
BUBBLE_LINE_HEIGHT = 20
BUBBLE_WIDTH = 260
BUBBLE_WRAP_WIDTH = 32
BUBBLE_FONT = ("Segoe UI", 10)
BUBBLE_FILL = "#252525"
BUBBLE_TEXT_COLOR = "#F0F0F0"
BUBBLE_TAIL_HEIGHT = 14
BUBBLE_RADIUS = 14
BUBBLE_SHADOW_OFFSET = 3

MOOD_BORDER_COLORS = {
    "happy": "#7EC8E3",
    "angry": "#E38B7E",
    "sick": "#9BB89B",
    "idle": "#666666",
}


def _round_rect(canvas, x1, y1, x2, y2, radius=14, **kwargs):
    """Draw a rounded rectangle using a smooth polygon."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)


def compute_bubble_geometry(text):
    """
    Given raw roast text, return (wrapped_text, bubble_width, bubble_height,
    window_width, window_height). window_width/height include room for the
    shadow offset and tail - use these to size the hosting Toplevel exactly.
    """
    wrapped = textwrap.fill(text, width=BUBBLE_WRAP_WIDTH, break_long_words=False)
    lines = wrapped.count("\n") + 1
    bubble_height = max(58, BUBBLE_PADDING * 2 + lines * BUBBLE_LINE_HEIGHT)
    bubble_width = BUBBLE_WIDTH

    window_width = bubble_width + BUBBLE_SHADOW_OFFSET + 4
    window_height = bubble_height + BUBBLE_TAIL_HEIGHT + BUBBLE_SHADOW_OFFSET + 4

    return wrapped, bubble_width, bubble_height, window_width, window_height


def render_bubble(canvas, wrapped_text, bubble_width, bubble_height,
                  mood="idle", show_cursor=False):
    """
    Dark-theme bubble with mood-colored border and a tail pointing down.
    show_cursor appends a blinking '|' — caller controls blink timing.
    """
    canvas.delete("bubble")

    border = MOOD_BORDER_COLORS.get(mood, MOOD_BORDER_COLORS["idle"])
    x1, y1 = 0, 0
    x2, y2 = bubble_width, bubble_height

    # Shadow
    _round_rect(
        canvas, x1 + BUBBLE_SHADOW_OFFSET, y1 + BUBBLE_SHADOW_OFFSET,
        x2 + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_SHADOW_OFFSET,
        radius=BUBBLE_RADIUS, fill="#000000", outline="", tags="bubble"
    )

    # Body
    _round_rect(
        canvas, x1, y1, x2, y2,
        radius=BUBBLE_RADIUS, fill=BUBBLE_FILL, outline=border,
        width=2, tags="bubble"
    )

    # Tail (pointing down toward pet)
    tcx = bubble_width // 2
    canvas.create_polygon(
        tcx - 10, y2, tcx + 10, y2, tcx, y2 + BUBBLE_TAIL_HEIGHT,
        fill=BUBBLE_FILL, outline=border, width=2, tags="bubble"
    )
    # Inner fill to hide the outline joint
    canvas.create_polygon(
        tcx - 8, y2, tcx + 8, y2, tcx, y2 + BUBBLE_TAIL_HEIGHT - 2,
        fill=BUBBLE_FILL, outline="", tags="bubble"
    )

    # Text + optional cursor
    display = wrapped_text + ("|" if show_cursor else "")
    canvas.create_text(
        bubble_width // 2, bubble_height // 2,
        text=display, width=bubble_width - 28,
        font=BUBBLE_FONT, fill=BUBBLE_TEXT_COLOR, justify="center",
        tags="bubble"
    )
