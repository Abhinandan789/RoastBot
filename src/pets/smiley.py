"""smiley.py - The original flat-circle smiley pet design."""

import math

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2
BASE_RADIUS = 42

MOOD_FILL_COLORS = {
    "happy": "#FFE4B5",
    "angry": "#FF6B6B",
    "sick": "#A8C0A0",
    "idle": "#E8D8C0"
}


def _clear(canvas):
    canvas.delete("pet")


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    bob_offset = math.sin(tick / 10) * 3
    y = CENTER_Y + bob_offset
    canvas.create_oval(
        CENTER_X - BASE_RADIUS, y - BASE_RADIUS,
        CENTER_X + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["idle"], outline=tone_color, width=3, tags="pet"
    )
    blink = (tick % 60) < 4
    eye_h = 3 if blink else 8
    for dx in (-15, 15):
        canvas.create_oval(
            CENTER_X + dx - 4, y - 9 - eye_h // 2,
            CENTER_X + dx + 4, y - 9 + eye_h // 2,
            fill="black", tags="pet"
        )


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    y = CENTER_Y - bounce
    canvas.create_oval(
        CENTER_X - BASE_RADIUS, y - BASE_RADIUS,
        CENTER_X + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["happy"], outline=tone_color, width=3, tags="pet"
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


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick / 2) * 4
    x = CENTER_X + shake
    y = CENTER_Y
    canvas.create_oval(
        x - BASE_RADIUS, y - BASE_RADIUS,
        x + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["angry"], outline=tone_color, width=3, tags="pet"
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
    canvas.create_line(x - 12, y + 12, x + 12, y + 8, width=3, fill="black", tags="pet")


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 20) * 5
    x = CENTER_X + sway
    y = CENTER_Y + 5
    canvas.create_oval(
        x - BASE_RADIUS, y - BASE_RADIUS,
        x + BASE_RADIUS, y + BASE_RADIUS,
        fill=MOOD_FILL_COLORS["sick"], outline=tone_color, width=3, tags="pet"
    )
    for dx in (-15, 15):
        canvas.create_line(x + dx - 5, y - 7, x + dx + 5, y - 7, width=3, fill="black", tags="pet")
    canvas.create_line(x - 10, y + 14, x + 10, y + 14, width=2, fill="black", tags="pet")