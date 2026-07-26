"""
pet_animations.py - Pure drawing logic for the desktop pet.

Single responsibility: given a Tkinter canvas, a mood, a tone bucket, and
a "tick" (an incrementing frame counter), draw the correct pose. No window
management, no polling, no file access happens here - this file only
knows how to draw, nothing about when or why.

Swappable later: if real sprite art replaces these procedural shapes,
only this file changes. pet_widget.py never needs to know the difference.
"""

import math

CANVAS_SIZE = 150
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2
BASE_RADIUS = 40

TONE_COLORS = {
    "warm": "#FFD700",       # gold glow
    "neutral": "#8B8B8B",    # neutral gray
    "cynical": "#5C6B73",    # cold slate
    "checked_out": "#3A3A3A"  # near-flat gray
}

MOOD_FILL_COLORS = {
    "happy": "#FFE4B5",
    "angry": "#FF6B6B",
    "sick": "#A8C0A0",
    "idle": "#E8D8C0"
}


def get_tone_color(tone_bucket):
    """Return the border/glow color for a given respect tone bucket."""
    return TONE_COLORS.get(tone_bucket, TONE_COLORS["neutral"])


def _clear(canvas):
    canvas.delete("pet")


def draw_idle(canvas, tick, tone_bucket="neutral"):
    """Default idle pose: gentle bob + occasional blink."""
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

    blink = (tick % 60) < 4  # brief blink every ~60 ticks
    eye_h = 2 if blink else 8
    for dx in (-15, 15):
        canvas.create_oval(
            CENTER_X + dx - 4, y - 10 - eye_h // 2,
            CENTER_X + dx + 4, y - 10 + eye_h // 2,
            fill="black", tags="pet"
        )


def draw_happy(canvas, tick, tone_bucket="neutral"):
    """Happy pose: bigger bounce, upward curve mouth."""
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
            CENTER_X + dx - 4, y - 14, CENTER_X + dx + 4, y - 6,
            fill="black", tags="pet"
        )
    canvas.create_arc(
        CENTER_X - 15, y - 5, CENTER_X + 15, y + 15,
        start=200, extent=140, style="arc", width=3, tags="pet"
    )


def draw_angry(canvas, tick, tone_bucket="neutral"):
    """Angry pose: shake side to side, furrowed brows."""
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
            x + dx - 4, y - 10, x + dx + 4, y - 2,
            fill="black", tags="pet"
        )
        brow_dir = 1 if dx < 0 else -1
        canvas.create_line(
            x + dx - 8, y - 16, x + dx + 8, y - 16 + (4 * brow_dir),
            width=2, fill="black", tags="pet"
        )
    canvas.create_line(
        x - 12, y + 12, x + 12, y + 8,
        width=3, fill="black", tags="pet"
    )


def draw_sick(canvas, tick, tone_bucket="neutral"):
    """Sick pose: slow sway, dimmed color, drooping eyes."""
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
            x + dx - 5, y - 8, x + dx + 5, y - 8,
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
    """Dispatch to the correct draw function for the given mood."""
    draw_fn = MOOD_DRAW_FUNCTIONS.get(mood, draw_idle)
    draw_fn(canvas, tick, tone_bucket)


def draw_speech_bubble(canvas, text):
    """Draw a speech bubble above the pet with the given text (wrapped)."""
    canvas.delete("bubble")
    bubble_top = max(5, CENTER_Y - BASE_RADIUS - 55)
    canvas.create_rectangle(
        10, bubble_top, CANVAS_SIZE - 10, bubble_top + 45,
        fill="white", outline="black", width=2, tags="bubble"
    )
    canvas.create_polygon(
        CENTER_X - 8, bubble_top + 45,
        CENTER_X + 8, bubble_top + 45,
        CENTER_X, bubble_top + 55,
        fill="white", outline="black", tags="bubble"
    )
    canvas.create_text(
        CANVAS_SIZE // 2, bubble_top + 22,
        text=text, width=CANVAS_SIZE - 25, font=("Segoe UI", 8),
        tags="bubble"
    )


def clear_speech_bubble(canvas):
    canvas.delete("bubble")