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
# Speech bubble - canvas-agnostic, hosted in its own Toplevel by
# pet_widget.py (see BubbleWindow class there). Everything below draws
# starting at (0,0) of whatever canvas it's given.
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
        x1, y1
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


def render_bubble(canvas, wrapped_text, bubble_width, bubble_height, mood="idle", show_cursor=False):
    """
    Draws the bubble with a dark theme, mood-colored border, and a tail
    pointing down toward the pet. show_cursor appends a blinking '|' for
    the typing effect - caller controls the blink timing.
    """
    canvas.delete("bubble")

    border = MOOD_BORDER_COLORS.get(mood, MOOD_BORDER_COLORS["idle"])
    x1, y1 = 0, 0
    x2, y2 = bubble_width, bubble_height

    _round_rect(
        canvas, x1 + BUBBLE_SHADOW_OFFSET, y1 + BUBBLE_SHADOW_OFFSET,
        x2 + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_SHADOW_OFFSET,
        radius=BUBBLE_RADIUS, fill="#000000", outline="", tags="bubble"
    )

    _round_rect(
        canvas, x1, y1, x2, y2,
        radius=BUBBLE_RADIUS, fill=BUBBLE_FILL, outline=border, width=2, tags="bubble"
    )

    tail_cx = bubble_width // 2
    canvas.create_polygon(
        tail_cx - 10, y2, tail_cx + 10, y2, tail_cx, y2 + BUBBLE_TAIL_HEIGHT,
        fill=BUBBLE_FILL, outline=border, width=2, tags="bubble"
    )
    canvas.create_polygon(
        tail_cx - 8, y2, tail_cx + 8, y2, tail_cx, y2 + BUBBLE_TAIL_HEIGHT - 2,
        fill=BUBBLE_FILL, outline="", tags="bubble"
    )

    display_text = wrapped_text + ("|" if show_cursor else "")
    canvas.create_text(
        bubble_width // 2, bubble_height // 2,
        text=display_text, width=bubble_width - 28,
        font=BUBBLE_FONT, fill=BUBBLE_TEXT_COLOR, justify="center",
        tags="bubble"
    )