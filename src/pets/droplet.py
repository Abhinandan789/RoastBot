"""droplet.py - A rounded droplet-shaped pet, procedurally drawn.

Body is a teardrop silhouette (built from an oval + a triangular top)
rather than a plain circle - visually closer to the blue-droplet style
without needing any image assets.
"""

import math

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2
BODY_WIDTH = 70
BODY_HEIGHT = 80

MOOD_FILL_COLORS = {
    "happy": "#7EC8E3",
    "angry": "#E38B7E",
    "sick": "#9BB89B",
    "idle": "#8FD3E8"
}


def _clear(canvas):
    canvas.delete("pet")


def _draw_body(canvas, cx, cy, fill, tone_color):
    """Teardrop shape: pointed top, rounded bottom."""
    points = []
    for i in range(37):
        angle = math.radians(i * 10)
        r = BODY_WIDTH / 2 * (1 - 0.35 * math.cos(angle))
        px = cx + r * math.sin(angle)
        py = cy + BODY_HEIGHT / 2 * (1 - math.cos(angle)) - BODY_HEIGHT / 2
        points.extend([px, py])
    canvas.create_polygon(points, fill=fill, outline=tone_color, width=3, smooth=True, tags="pet")


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    bob = math.sin(tick / 10) * 3
    y = CENTER_Y + bob
    _draw_body(canvas, CENTER_X, y, MOOD_FILL_COLORS["idle"], tone_color)
    blink = (tick % 70) < 4
    eye_h = 3 if blink else 9
    for dx in (-12, 12):
        canvas.create_oval(
            CENTER_X + dx - 5, y - 5 - eye_h // 2,
            CENTER_X + dx + 5, y - 5 + eye_h // 2,
            fill="black", tags="pet"
        )
    for dx in (-12, 12):
        canvas.create_oval(
            CENTER_X + dx - 8, y + 12, CENTER_X + dx - 2, y + 18,
            fill="#F4A6A0", outline="", tags="pet"
        )


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 12
    y = CENTER_Y - bounce
    _draw_body(canvas, CENTER_X, y, MOOD_FILL_COLORS["happy"], tone_color)
    for dx in (-12, 12):
        canvas.create_arc(
            CENTER_X + dx - 6, y - 10, CENTER_X + dx + 6, y,
            start=0, extent=180, style="arc", width=2, tags="pet"
        )
    canvas.create_arc(
        CENTER_X - 14, y + 2, CENTER_X + 14, y + 20,
        start=200, extent=140, style="arc", width=3, tags="pet"
    )
    for dx in (-12, 12):
        canvas.create_oval(
            CENTER_X + dx - 8, y + 10, CENTER_X + dx - 2, y + 16,
            fill="#F4A6A0", outline="", tags="pet"
        )


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick / 2) * 4
    x = CENTER_X + shake
    y = CENTER_Y
    _draw_body(canvas, x, y, MOOD_FILL_COLORS["angry"], tone_color)
    for dx in (-12, 12):
        canvas.create_oval(x + dx - 5, y - 8, x + dx + 5, y, fill="black", tags="pet")
        brow_dir = 1 if dx < 0 else -1
        canvas.create_line(
            x + dx - 9, y - 14, x + dx + 9, y - 14 + (4 * brow_dir),
            width=2, fill="black", tags="pet"
        )
    canvas.create_line(x - 12, y + 14, x + 12, y + 10, width=3, fill="black", tags="pet")


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 20) * 5
    x = CENTER_X + sway
    y = CENTER_Y + 5
    _draw_body(canvas, x, y, MOOD_FILL_COLORS["sick"], tone_color)
    for dx in (-12, 12):
        canvas.create_line(x + dx - 6, y - 5, x + dx + 6, y - 5, width=3, fill="black", tags="pet")
    canvas.create_line(x - 10, y + 16, x + 10, y + 16, width=2, fill="black", tags="pet")