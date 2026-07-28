"""ghost.py - Cute floating ghost with wavy hem, big eyes, and tiny arms."""

import math
import random

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2

GHOST_W = 64
GHOST_H = 78

MOOD_FILL = {
    "idle":  "#F0F0F0",
    "happy": "#E8F4FF",
    "angry": "#FFB8B8",
    "sick":  "#D4E8D4",
}

# ------------------------------------------------------------------
#  Interactivity state (shared across frames)
# ------------------------------------------------------------------
_hover_scale = 1.0
_squish = 0.0


def _clear(canvas):
    canvas.delete("pet")


def _ghost_body(canvas, cx, cy, mood, tick, scale=1.0):
    fill = MOOD_FILL[mood]
    outline = "#555555" if mood != "angry" else "#AA4444"

    w = GHOST_W * scale
    h = GHOST_H * scale

    # Build full outline as a single polygon
    pts = []

    # Top dome: left to right (180° to 0°)
    for i in range(21):
        a = math.radians(180 - i * 9)  # 180 down to 0
        px = cx + (w / 2) * math.cos(a)
        py = cy - 10 * scale - (w / 2) * math.sin(a)
        pts.extend([px, py])

    # Right side down to bottom-right
    pts.extend([cx + w / 2, cy + 10 * scale])

    # Wavy bottom edge: right to left
    waves = 5
    for i in range(waves + 1):
        t = i / waves
        px = (cx + w / 2) - w * t
        py = cy + h / 2 + math.sin(tick / 8 + t * 4) * 3
        pts.extend([px, py])

    # Left side up to close
    pts.extend([cx - w / 2, cy + 10 * scale])

    canvas.create_polygon(
        pts, fill=fill, outline=outline, width=3,
        smooth=True, tags="pet"
    )


def _arms(canvas, cx, cy, mood, tick, scale=1.0):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 8
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 42 * scale, cy - 15 * scale + wave,
                cx + side * 54 * scale, cy - 5 * scale + wave,
                fill=fill, outline="#555", width=2, tags="pet"
            )
    else:
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 40 * scale, cy + 5 * scale,
                cx + side * 52 * scale, cy + 18 * scale,
                fill=fill, outline="#555", width=2, tags="pet"
            )


def _track_pupil(canvas, eye_cx, eye_cy, max_off=5):
    """Track mouse with random gaze: follow for a bit, then rest at center."""
    from src.pet_animations import track_mouse
    return track_mouse(canvas, eye_cx, eye_cy, max_offset=max_off)


def _eyes(canvas, cx, cy, mood, tick, scale=1.0):
    # Random natural blink
    blink = random.random() < 0.005 or (tick % 150 < 4 and random.random() < 0.3)

    if blink:
        for dx in (-14, 14):
            canvas.create_line(
                cx + dx * scale - 6 * scale, cy - 8 * scale,
                cx + dx * scale + 6 * scale, cy - 8 * scale,
                width=3, fill="#222", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx * scale - 8 * scale, cy - 14 * scale,
                cx + dx * scale + 8 * scale, cy - 2 * scale,
                start=0, extent=180, style="arc", width=3,
                outline="#222", tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-14, 14):
            canvas.create_oval(
                cx + dx * scale - 5 * scale, cy - 12 * scale,
                cx + dx * scale + 5 * scale, cy - 2 * scale,
                fill="#222", outline="", tags="pet"
            )
            slope = 1 if dx < 0 else -1
            canvas.create_line(
                cx + dx * scale - 8 * scale, cy - 18 * scale,
                cx + dx * scale + 6 * scale, cy - 14 * scale + (3 * slope),
                width=3, fill="#222", tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx * scale - 8 * scale, cy - 10 * scale,
                cx + dx * scale + 8 * scale, cy,
                start=180, extent=180, style="arc", width=3,
                outline="#222", tags="pet"
            )
        return

    # Normal big cute eyes — with mouse-tracking pupils (via random gaze)
    for dx in (-14, 14):
        ex = cx + dx * scale
        ey = cy - 6 * scale
        # Sclera
        canvas.create_oval(
            ex - 8 * scale, ey - 8 * scale,
            ex + 8 * scale, ey + 8 * scale,
            fill="white", outline="#222", width=2, tags="pet"
        )
        # Pupil follows mouse (with random gaze pauses)
        px, py = _track_pupil(canvas, ex, ey, max_off=5 * scale)
        canvas.create_oval(
            px - 3 * scale, py - 3 * scale,
            px + 3 * scale, py + 3 * scale,
            fill="#222", outline="", tags="pet"
        )
        # Shine
        canvas.create_oval(
            px - 2 * scale, py - 5 * scale,
            px, py - 3 * scale,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood, scale=1.0):
    if mood == "happy":
        canvas.create_arc(
            cx - 10 * scale, cy + 2 * scale,
            cx + 10 * scale, cy + 18 * scale,
            start=200, extent=140, style="arc", width=3,
            outline="#222", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 10 * scale, cy + 10 * scale,
            cx + 10 * scale, cy + 6 * scale,
            width=3, fill="#222", tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            cx - 8 * scale, cy + 6 * scale,
            cx + 8 * scale, cy + 18 * scale,
            start=20, extent=140, style="arc", width=3,
            outline="#222", tags="pet"
        )
    else:
        canvas.create_oval(
            cx - 3 * scale, cy + 6 * scale,
            cx + 3 * scale, cy + 12 * scale,
            fill="#222", outline="", tags="pet"
        )


def _cheeks(canvas, cx, cy, mood, scale=1.0):
    if mood in ("happy", "idle"):
        for dx in (-22, 22):
            canvas.create_oval(
                cx + dx * scale - 6 * scale, cy - 2 * scale,
                cx + dx * scale + 2 * scale, cy + 6 * scale,
                fill="#FFB8C9", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick, scale=1.0):
    if mood == "happy":
        for i in range(3):
            sx = cx + math.sin(tick / 8 + i * 2) * 50 * scale
            sy = cy - 50 * scale + i * 12
            canvas.create_text(
                sx, sy, text="✦", fill="#B8E0FF",
                font=("Arial", 10, "bold"), tags="pet"
            )

    elif mood == "angry":
        canvas.create_text(
            cx + 40 * scale, cy - 38 * scale, text="boo",
            font=("Arial", 12, "bold"), fill="#AA4444", tags="pet"
        )
        for side in (-1, 1):
            canvas.create_line(
                cx + side * 50 * scale, cy - 4 * scale,
                cx + side * 64 * scale, cy - 10 * scale,
                width=2, fill="#AA4444", tags="pet"
            )

    elif mood == "sick":
        canvas.create_polygon(
            cx + 24 * scale, cy - 22 * scale,
            cx + 30 * scale, cy - 8 * scale,
            cx + 18 * scale, cy - 8 * scale,
            fill="#79CFFF", outline="", tags="pet"
        )
        if (tick // 14) % 2 == 0:
            canvas.create_text(
                cx - 36 * scale, cy - 42 * scale, text="✦", fill="#C8E6C9",
                font=("Arial", 10), tags="pet"
            )


def _draw_pet(canvas, cx, cy, mood, tick, scale=1.0):
    _arms(canvas, cx, cy, mood, tick, scale)
    _ghost_body(canvas, cx, cy, mood, tick, scale)
    _eyes(canvas, cx, cy, mood, tick, scale)
    _mouth(canvas, cx, cy, mood, scale)
    _cheeks(canvas, cx, cy, mood, scale)
    _mood_fx(canvas, cx, cy, mood, tick, scale)


def _update_interactivity(canvas):
    """Check hover/click on canvas to drive scale and squish."""
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
    if not getattr(canvas, "_ghost_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._ghost_click_bound = True


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    hover = math.sin(tick / 18) * 3
    _draw_pet(canvas, CENTER_X, CENTER_Y + hover, "idle", tick, scale)
    _bind_click_once(canvas)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bounce = abs(math.sin(tick / 6)) * 12
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick, scale)
    _bind_click_once(canvas)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    shake = math.sin(tick * 0.9) * 4
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick, scale)
    _bind_click_once(canvas)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 22) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 4, "sick", tick, scale)
    _bind_click_once(canvas)
