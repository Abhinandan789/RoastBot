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


def _clear(canvas):
    canvas.delete("pet")


def draw_idle(canvas, tick, tone_bucket="neutral"):
    _clear(canvas)
    bob_offset = math.sin(tick / 10) * 3
    y = CENTER_Y + bob_offset
    border_color = get_tone_color(tone_bucket)

    canvas.create_oval(
        CENTER_X - BASE_RADIUS, y - BASE_RADIUS,
        CENTER_X + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["idle"], outline=border_color, width=3,
        tags="pet"
    )

    blink = (tick % 60) < 4
    eye_h = 3 if blink else 8
    for dx in (-15, 15):
        canvas.create_oval(
            CENTER_X + dx - 4, y - 9 - eye_h // 2,
            CENTER_X + dx + 4, y - 9 + eye_h // 2,
            fill="black", tags="pet"
        )


def draw_happy(canvas, tick, tone_bucket="neutral"):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    y = CENTER_Y - bounce
    border_color = get_tone_color(tone_bucket)

    canvas.create_oval(
        CENTER_X - BASE_RADIUS, y - BASE_RADIUS,
        CENTER_X + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["happy"], outline=border_color, width=3,
        tags="pet"
    )
    for dx in (-15, 15):
        canvas.create_oval(
            CENTER_X + dx - 4, y - 13, CENTER_X + dx + 4, y - 5,
            fill="black", tags="pet"
        )
    canvas.create_arc(
        CENTER_X - 15, y - 5, CENTER_X + 15, y + 15,
        start=200, extent=140, style="arc", width=3, tags="pet"
    )


def draw_angry(canvas, tick, tone_bucket="neutral"):
    _clear(canvas)
    shake = math.sin(tick / 2) * 4
    x = CENTER_X + shake
    y = CENTER_Y
    border_color = get_tone_color(tone_bucket)

    canvas.create_oval(
        x - BASE_RADIUS, y - BASE_RADIUS,
        x + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["angry"], outline=border_color, width=3,
        tags="pet"
    )
    for dx in (-15, 15):
        canvas.create_oval(
            x + dx - 4, y - 9, x + dx + 4, y - 1,
            fill="black", tags="pet"
        )
        brow_dir = 1 if dx < 0 else -1
        canvas.create_line(
            x + dx - 8, y - 15, x + dx + 8, y - 15 + (4 * brow_dir),
            width=2, fill="black", tags="pet"
        )
    canvas.create_line(
        x - 12, y + 12, x + 12, y + 8,
        width=3, fill="black", tags="pet"
    )


def draw_sick(canvas, tick, tone_bucket="neutral"):
    _clear(canvas)
    sway = math.sin(tick / 20) * 5
    x = CENTER_X + sway
    y = CENTER_Y + 5
    border_color = get_tone_color(tone_bucket)

    canvas.create_oval(
        x - BASE_RADIUS, y - BASE_RADIUS,
        x + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["sick"], outline=border_color, width=3,
        tags="pet"
    )
    for dx in (-15, 15):
        canvas.create_line(
            x + dx - 5, y - 7, x + dx + 5, y - 7,
            width=3, fill="black", tags="pet"
        )
    canvas.create_line(
        x - 10, y + 14, x + 10, y + 14,
        width=2, fill="black", tags="pet"
    )


MOOD_DRAW_FUNCTIONS = {
    "happy": draw_happy,
    "angry": draw_angry,
    "sick": draw_sick,
    "idle": draw_idle,
}


def draw_mood(canvas, mood, tick, tone_bucket="neutral"):
    draw_fn = MOOD_DRAW_FUNCTIONS.get(mood, draw_idle)
    draw_fn(canvas, tick, tone_bucket)


# ---------------------------------------------------------------------
# Speech bubble - canvas-agnostic, hosted in its own Toplevel by
# pet_widget.py (see BubbleWindow class there). Everything below draws
# starting at (0,0) of whatever canvas it's given.
# ---------------------------------------------------------------------

BUBBLE_PADDING = 14
BUBBLE_LINE_HEIGHT = 18
BUBBLE_WIDTH = 230
BUBBLE_WRAP_WIDTH = 28
BUBBLE_FONT = ("Segoe UI", 10)
BUBBLE_FILL = "#FFFDF8"
BUBBLE_BORDER = "#404040"
BUBBLE_SHADOW = "#BEBEBE"
BUBBLE_TEXT_COLOR = "#202020"
BUBBLE_TAIL_HEIGHT = 14
BUBBLE_RADIUS = 14
BUBBLE_SHADOW_OFFSET = 3


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


def render_bubble(canvas, wrapped_text, bubble_width, bubble_height):
    """
    Draw the full bubble (shadow, body, tail, text) onto a canvas sized
    exactly to window_width x window_height as returned by
    compute_bubble_geometry(). Drawing starts at (0,0).
    """
    canvas.delete("bubble")

    x1, y1 = 0, 0
    x2, y2 = bubble_width, bubble_height

    _round_rect(
        canvas, x1 + BUBBLE_SHADOW_OFFSET, y1 + BUBBLE_SHADOW_OFFSET,
        x2 + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_SHADOW_OFFSET,
        radius=BUBBLE_RADIUS, fill=BUBBLE_SHADOW, outline="", tags="bubble"
    )

    _round_rect(
        canvas, x1, y1, x2, y2,
        radius=BUBBLE_RADIUS, fill=BUBBLE_FILL, outline=BUBBLE_BORDER,
        width=2, tags="bubble"
    )

    tail_cx = bubble_width // 2

    canvas.create_polygon(
        tail_cx + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_SHADOW_OFFSET,
        tail_cx - 8 + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_TAIL_HEIGHT + BUBBLE_SHADOW_OFFSET,
        tail_cx + 8 + BUBBLE_SHADOW_OFFSET, y2 + BUBBLE_TAIL_HEIGHT + BUBBLE_SHADOW_OFFSET,
        fill=BUBBLE_SHADOW, outline="", tags="bubble"
    )

    canvas.create_polygon(
        tail_cx, y2,
        tail_cx - 8, y2 + BUBBLE_TAIL_HEIGHT,
        tail_cx + 8, y2 + BUBBLE_TAIL_HEIGHT,
        fill=BUBBLE_FILL, outline=BUBBLE_BORDER, width=2, tags="bubble"
    )

    canvas.create_text(
        bubble_width // 2, bubble_height // 2,
        text=wrapped_text, width=bubble_width - 28,
        font=BUBBLE_FONT, fill=BUBBLE_TEXT_COLOR, justify="center",
        tags="bubble"
    )