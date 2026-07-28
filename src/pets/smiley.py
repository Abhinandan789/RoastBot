"""smiley.py - The original flat-circle smiley pet design."""

import math
import random

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

_hover_scale = 1.0
_squish = 0.0


def _clear(canvas):
    canvas.delete("pet")


def _update_interactivity(canvas):
    global _hover_scale, _squish
    try:
        mx = canvas.winfo_pointerx() - canvas.winfo_rootx()
        my = canvas.winfo_pointery() - canvas.winfo_rooty()
        in_bounds = 50 < mx < 170 and 50 < my < 170
    except Exception:
        in_bounds = False

    target = 1.08 if in_bounds else 1.0
    _hover_scale += (target - _hover_scale) * 0.15
    _squish *= 0.85
    if _squish < 0.01:
        _squish = 0.0
    return _hover_scale * (1 - _squish), _squish


def _on_click(event):
    global _squish
    _squish = 0.25


def _bind_click_once(canvas):
    if not getattr(canvas, "_smiley_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._smiley_click_bound = True


def _track_eye(canvas, eye_cx, eye_cy, max_off=2):
    from src.pet_animations import track_mouse
    return track_mouse(canvas, eye_cx, eye_cy, max_offset=max_off)


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bob_offset = math.sin(tick / 10) * 3
    y = CENTER_Y + bob_offset
    r = BASE_RADIUS * scale

    canvas.create_oval(
        CENTER_X - r, y - r,
        CENTER_X + r, y + r,
        fill=MOOD_FILL_COLORS["idle"], outline=tone_color, width=3, tags="pet"
    )

    blink = random.random() < 0.005 or (tick % 140 < 4 and random.random() < 0.3)
    eye_h = 3 if blink else 8 * scale

    for dx in (-15, 15):
        ex = CENTER_X + dx * scale
        ey = y - 9 * scale
        px, py = _track_eye(canvas, ex, ey, max_off=2 * scale)
        canvas.create_oval(
            px - 4 * scale, py - eye_h // 2,
            px + 4 * scale, py + eye_h // 2,
            fill="black", tags="pet"
        )

    _bind_click_once(canvas)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    y = CENTER_Y - bounce
    r = BASE_RADIUS * scale

    canvas.create_oval(
        CENTER_X - r, y - r,
        CENTER_X + r, y + r,
        fill=MOOD_FILL_COLORS["happy"], outline=tone_color, width=3, tags="pet"
    )
    for dx in (-15, 15):
        ex = CENTER_X + dx * scale
        ey = y - 9 * scale
        px, py = _track_eye(canvas, ex, ey, max_off=2 * scale)
        canvas.create_oval(
            px - 4 * scale, py - 4 * scale,
            px + 4 * scale, py + 4 * scale,
            fill="black", tags="pet"
        )
    canvas.create_arc(
        CENTER_X - 15 * scale, y - 5 * scale,
        CENTER_X + 15 * scale, y + 15 * scale,
        start=200, extent=140, style="arc", width=3, tags="pet"
    )
    _bind_click_once(canvas)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    shake = math.sin(tick / 2) * 4
    x = CENTER_X + shake
    y = CENTER_Y
    r = BASE_RADIUS * scale

    canvas.create_oval(
        x - r, y - r,
        x + r, y + r,
        fill=MOOD_FILL_COLORS["angry"], outline=tone_color, width=3, tags="pet"
    )
    for dx in (-15, 15):
        ex = x + dx * scale
        ey = y - 9 * scale
        px, py = _track_eye(canvas, ex, ey, max_off=2 * scale)
        canvas.create_oval(
            px - 4 * scale, py - 4 * scale,
            px + 4 * scale, py + 4 * scale,
            fill="black", tags="pet"
        )
        brow_dir = 1 if dx < 0 else -1
        canvas.create_line(
            px - 8 * scale, y - 15 * scale,
            px + 8 * scale, y - 15 * scale + (4 * scale * brow_dir),
            width=2, fill="black", tags="pet"
        )
    canvas.create_line(x - 12 * scale, y + 12 * scale,
                       x + 12 * scale, y + 8 * scale,
                       width=3, fill="black", tags="pet")
    _bind_click_once(canvas)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 20) * 5
    x = CENTER_X + sway
    y = CENTER_Y + 5
    r = BASE_RADIUS * scale

    canvas.create_oval(
        x - r, y - r,
        x + r, y + r,
        fill=MOOD_FILL_COLORS["sick"], outline=tone_color, width=3, tags="pet"
    )
    for dx in (-15, 15):
        ex = x + dx * scale
        ey = y - 7 * scale
        px, py = _track_eye(canvas, ex, ey, max_off=2 * scale)
        canvas.create_line(px - 5 * scale, py, px + 5 * scale, py,
                           width=3, fill="black", tags="pet")
    canvas.create_line(x - 10 * scale, y + 14 * scale,
                       x + 10 * scale, y + 14 * scale,
                       width=2, fill="black", tags="pet")
    _bind_click_once(canvas)
