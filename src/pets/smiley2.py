"""smiley2.py - 3D-ish smiley with hands, pupils, cheeks, and shadow."""

import math
import random

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2
R = 46

MOOD_FILL = {
    "idle":  "#F2D9A0",
    "happy": "#FFD27D",
    "angry": "#E86B5C",
    "sick":  "#A8C0A0",
}

MOOD_SHADE = {
    "idle":  "#E8C994",
    "happy": "#F2C25C",
    "angry": "#D45A4A",
    "sick":  "#94A88E",
}

_hover_scale = 1.0
_squish = 0.0


def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, cx, cy, scale=1.0):
    canvas.create_oval(
        cx - 44 * scale, cy + 38 * scale,
        cx + 44 * scale, cy + 52 * scale,
        fill="#1A1A1A", outline="", tags="pet"
    )


def _face(canvas, cx, cy, mood, scale=1.0):
    fill = MOOD_FILL[mood]
    shade = MOOD_SHADE[mood]

    canvas.create_oval(
        cx - R * scale, cy - R * scale,
        cx + R * scale, cy + R * scale,
        fill=fill, outline="#3A3A3A", width=3, tags="pet"
    )
    canvas.create_arc(
        cx - R * scale + 4, cy - R * scale + 4,
        cx + R * scale - 2, cy + R * scale - 2,
        start=260, extent=120, style="arc", width=8,
        outline=shade, tags="pet"
    )
    canvas.create_oval(
        cx - 28 * scale, cy - 36 * scale,
        cx - 8 * scale, cy - 16 * scale,
        fill="white", outline="", tags="pet"
    )


def _hands(canvas, cx, cy, mood, tick, scale=1.0):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 8
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 52 * scale, cy - 15 * scale + wave,
                cx + side * 66 * scale, cy - 5 * scale + wave,
                fill=fill, outline="#3A3A3A", width=2, tags="pet"
            )
    else:
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 50 * scale, cy + 5 * scale,
                cx + side * 62 * scale, cy + 20 * scale,
                fill=fill, outline="#3A3A3A", width=2, tags="pet"
            )


def _track_pupil(canvas, eye_cx, eye_cy, max_off=4):
    from src.pet_animations import track_mouse
    return track_mouse(canvas, eye_cx, eye_cy, max_offset=max_off)


def _eyes(canvas, cx, cy, mood, tick, scale=1.0):
    blink = random.random() < 0.005 or (tick % 130 < 5 and random.random() < 0.3)

    if blink:
        for dx in (-16, 16):
            canvas.create_line(
                cx + dx * scale - 7 * scale, cy - 4 * scale,
                cx + dx * scale + 7 * scale, cy - 4 * scale,
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-16, 16):
            canvas.create_arc(
                cx + dx * scale - 8 * scale, cy - 10 * scale,
                cx + dx * scale + 8 * scale, cy + 4 * scale,
                start=0, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-16, 16):
            canvas.create_oval(
                cx + dx * scale - 5 * scale, cy - 8 * scale,
                cx + dx * scale + 5 * scale, cy + 6 * scale,
                fill="#1A1A1A", outline="", tags="pet"
            )
            slope = 1 if dx < 0 else -1
            canvas.create_line(
                cx + dx * scale - 9 * scale, cy - 14 * scale,
                cx + dx * scale + 7 * scale, cy - 10 * scale + (3 * slope),
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-16, 16):
            canvas.create_arc(
                cx + dx * scale - 8 * scale, cy - 4 * scale,
                cx + dx * scale + 8 * scale, cy + 8 * scale,
                start=180, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    for dx in (-16, 16):
        ex = cx + dx * scale
        ey = cy
        canvas.create_oval(
            ex - 7 * scale, ey - 10 * scale,
            ex + 7 * scale, ey + 10 * scale,
            fill="white", outline="#3A3A3A", width=1, tags="pet"
        )
        px, py = _track_pupil(canvas, ex, ey, max_off=4 * scale)
        canvas.create_oval(
            px - 3 * scale, py - 4 * scale,
            px + 1 * scale, py + 2 * scale,
            fill="#1A1A1A", outline="", tags="pet"
        )
        canvas.create_oval(
            px - 2 * scale, py - 6 * scale,
            px, py - 4 * scale,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood, scale=1.0):
    if mood == "happy":
        canvas.create_arc(
            cx - 16 * scale, cy + 2 * scale,
            cx + 16 * scale, cy + 26 * scale,
            start=200, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
        canvas.create_oval(
            cx - 6 * scale, cy + 16 * scale,
            cx + 6 * scale, cy + 24 * scale,
            fill="#F4A6A0", outline="", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 12 * scale, cy + 16 * scale,
            cx + 12 * scale, cy + 12 * scale,
            width=3, fill="#1A1A1A", tags="pet"
        )
        canvas.create_line(
            cx - 8 * scale, cy + 14 * scale,
            cx + 8 * scale, cy + 14 * scale,
            width=2, fill="#DDD", tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            cx - 10 * scale, cy + 12 * scale,
            cx + 10 * scale, cy + 26 * scale,
            start=20, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
        canvas.create_oval(
            cx - 4 * scale, cy + 18 * scale,
            cx + 4 * scale, cy + 28 * scale,
            fill="#E88B9B", outline="", tags="pet"
        )
    else:
        canvas.create_arc(
            cx - 8 * scale, cy + 8 * scale,
            cx + 8 * scale, cy + 20 * scale,
            start=200, extent=140, style="arc", width=2,
            outline="#1A1A1A", tags="pet"
        )


def _cheeks(canvas, cx, cy, mood, scale=1.0):
    if mood in ("happy", "idle"):
        for dx in (-26, 26):
            canvas.create_oval(
                cx + dx * scale - 7 * scale, cy + 4 * scale,
                cx + dx * scale + 1 * scale, cy + 12 * scale,
                fill="#F4A6A0", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick, scale=1.0):
    if mood == "happy":
        for i in range(3):
            sx = cx + math.sin(tick / 8 + i * 2) * 55 * scale
            sy = cy - 55 * scale + i * 12
            canvas.create_text(
                sx, sy, text="✦", fill="#FFD95A",
                font=("Arial", 10, "bold"), tags="pet"
            )
    elif mood == "angry":
        canvas.create_line(
            cx - 30 * scale, cy - 28 * scale,
            cx - 20 * scale, cy - 32 * scale,
            width=2, fill="#D45A4A", tags="pet"
        )
        canvas.create_line(
            cx + 20 * scale, cy - 32 * scale,
            cx + 30 * scale, cy - 28 * scale,
            width=2, fill="#D45A4A", tags="pet"
        )
        canvas.create_text(
            cx + 45 * scale, cy - 42 * scale, text="mad",
            font=("Arial", 12, "bold"), fill="#D45A4A", tags="pet"
        )
        for side in (-1, 1):
            canvas.create_line(
                cx + side * 56 * scale, cy - 6 * scale,
                cx + side * 72 * scale, cy - 14 * scale,
                width=2, fill="#3A3A3A", tags="pet"
            )
            canvas.create_line(
                cx + side * 56 * scale, cy + 10 * scale,
                cx + side * 74 * scale, cy + 18 * scale,
                width=2, fill="#3A3A3A", tags="pet"
            )
    elif mood == "sick":
        canvas.create_polygon(
            cx + 28 * scale, cy - 26 * scale,
            cx + 34 * scale, cy - 12 * scale,
            cx + 22 * scale, cy - 12 * scale,
            fill="#79CFFF", outline="", tags="pet"
        )
        canvas.create_arc(
            cx - 16 * scale, cy - 30 * scale,
            cx + 16 * scale, cy - 8 * scale,
            start=0, extent=180, fill="#C8E6C9", outline="", tags="pet"
        )
        canvas.create_text(
            cx - 42 * scale, cy - 48 * scale, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )
        canvas.create_text(
            cx + 44 * scale, cy - 46 * scale, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )


def _draw_pet(canvas, cx, cy, mood, tick, scale=1.0):
    _shadow(canvas, cx, cy, scale)
    _hands(canvas, cx, cy, mood, tick, scale)
    _face(canvas, cx, cy, mood, scale)
    _eyes(canvas, cx, cy, mood, tick, scale)
    _mouth(canvas, cx, cy, mood, scale)
    _cheeks(canvas, cx, cy, mood, scale)
    _mood_fx(canvas, cx, cy, mood, tick, scale)


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
    if not getattr(canvas, "_smiley2_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._smiley2_click_bound = True


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bob = math.sin(tick / 16) * 2.5
    _draw_pet(canvas, CENTER_X, CENTER_Y + bob, "idle", tick, scale)
    _bind_click_once(canvas)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick, scale)
    _bind_click_once(canvas)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    shake = math.sin(tick * 0.85) * 4
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick, scale)
    _bind_click_once(canvas)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 20) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 5, "sick", tick, scale)
    _bind_click_once(canvas)
