"""droplet.py - Living droplet that watches you."""

import math
import random

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2

BODY_W = 74
BODY_H = 88

MOOD_FILL = {
    "idle":  "#8FD3E8",
    "happy": "#7EC8E3",
    "angry": "#E38B7E",
    "sick":  "#9BB89B",
}

MOOD_GLOW = {
    "idle":  "#B8E6F5",
    "happy": "#A8E0F5",
    "angry": "#F5B8A8",
    "sick":  "#B8D4B8",
}


# ------------------------------------------------------------------
#  Interactivity state (shared across frames)
# ------------------------------------------------------------------
_hover_scale = 1.0
_squish = 0.0


def _clear(canvas):
    canvas.delete("pet")


def _teardrop_points(cx, cy, w, h):
    pts = []
    steps = 48
    for i in range(steps):
        t = (i / steps) * 2 * math.pi
        x = cx + math.sin(t) * (w / 2) * (1 - 0.4 * math.cos(t))
        y = cy - math.cos(t) * (h / 2)
        pts.extend([x, y])
    return pts


def _shadow(canvas, cx, cy):
    canvas.create_oval(
        cx - 36, cy + 38, cx + 36, cy + 50,
        fill="#1A1A1A", outline="", tags="pet"
    )


def _body(canvas, cx, cy, mood, scale=1.0):
    fill = MOOD_FILL[mood]
    glow = MOOD_GLOW[mood]

    # Apply hover scale
    w, h = BODY_W * scale, BODY_H * scale

    pts = _teardrop_points(cx, cy, w, h)
    canvas.create_polygon(
        pts, fill=fill, outline="#3A3A3A", width=3,
        smooth=True, tags="pet"
    )

    inner_pts = _teardrop_points(cx, cy + 4 * scale, w - 18, h - 18)
    canvas.create_polygon(
        inner_pts, fill=glow, outline="", smooth=True, tags="pet"
    )

    # Highlight
    canvas.create_oval(
        cx - 18 * scale, cy - 28 * scale, cx + 2 * scale, cy - 8 * scale,
        fill="white", outline="", tags="pet"
    )
    canvas.create_oval(
        cx - 10 * scale, cy - 24 * scale, cx - 2 * scale, cy - 16 * scale,
        fill="#FFFFFF", outline="", tags="pet"
    )


def _feet(canvas, cx, cy, mood, scale=1.0):
    fill = MOOD_FILL[mood]
    for dx in (-18, 18):
        canvas.create_oval(
            cx + dx - 10, cy + 32, cx + dx + 10, cy + 46,
            fill=fill, outline="#3A3A3A", width=2, tags="pet"
        )


def _track_pupil(canvas, eye_cx, eye_cy, max_off=4):
    try:
        mx = canvas.winfo_pointerx() - canvas.winfo_rootx()
        my = canvas.winfo_pointery() - canvas.winfo_rooty()
    except Exception:
        return eye_cx, eye_cy
    dx, dy = mx - eye_cx, my - eye_cy
    dist = math.hypot(dx, dy)
    if dist == 0:
        return eye_cx, eye_cy
    off = min(max_off, dist / 10)
    ang = math.atan2(dy, dx)
    return eye_cx + math.cos(ang) * off, eye_cy + math.sin(ang) * off


def _eyes(canvas, cx, cy, mood, tick, scale=1.0):
    # Random natural blink (not rigid modulo)
    blink = random.random() < 0.005 or (tick % 180 < 4 and random.random() < 0.3)

    if blink:
        for dx in (-14, 14):
            canvas.create_line(
                cx + dx - 6, cy - 4, cx + dx + 6, cy - 4,
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx - 7, cy - 10, cx + dx + 7, cy + 2,
                start=0, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-14, 14):
            canvas.create_oval(
                cx + dx - 5, cy - 8, cx + dx + 5, cy + 4,
                fill="#1A1A1A", outline="", tags="pet"
            )
            slope = 1 if dx < 0 else -1
            canvas.create_line(
                cx + dx - 8, cy - 14, cx + dx + 6, cy - 10 + (3 * slope),
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx - 7, cy - 4, cx + dx + 7, cy + 6,
                start=180, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    # Normal eyes — with mouse-tracking pupils
    for dx in (-14, 14):
        # Sclera
        canvas.create_oval(
            cx + dx - 6, cy - 8, cx + dx + 6, cy + 8,
            fill="white", outline="#3A3A3A", width=1, tags="pet"
        )
        # Pupil follows mouse
        px, py = _track_pupil(canvas, cx + dx, cy)
        canvas.create_oval(
            px - 3, py - 4, px + 1, py + 2,
            fill="#1A1A1A", outline="", tags="pet"
        )
        # Shine
        canvas.create_oval(
            px - 2, py - 6, px, py - 4,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood):
    if mood == "happy":
        canvas.create_arc(
            cx - 12, cy + 4, cx + 12, cy + 22,
            start=200, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 10, cy + 14, cx + 10, cy + 10,
            width=3, fill="#1A1A1A", tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            cx - 8, cy + 10, cx + 8, cy + 22,
            start=20, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
    else:
        canvas.create_arc(
            cx - 6, cy + 8, cx + 6, cy + 18,
            start=200, extent=140, style="arc", width=2,
            outline="#1A1A1A", tags="pet"
        )


def _cheeks(canvas, cx, cy, mood):
    if mood in ("happy", "idle"):
        for dx in (-22, 22):
            canvas.create_oval(
                cx + dx - 6, cy + 4, cx + dx + 2, cy + 12,
                fill="#F4A6A0", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick):
    if mood == "happy":
        for i in range(3):
            sx = cx + math.sin(tick / 8 + i * 2.1) * 52
            sy = cy - 55 + i * 14
            canvas.create_text(
                sx, sy, text="✦", fill="#FFD95A",
                font=("Arial", 10, "bold"), tags="pet"
            )
        if (tick // 18) % 3 == 0:
            canvas.create_text(
                cx + 45, cy - 50, text="♥",
                fill="#FF6B8A", font=("Arial", 11, "bold"), tags="pet"
            )

    elif mood == "angry":
        for side in (-1, 1):
            px = cx + side * 28
            py = cy - 42 - (tick % 20) * 0.8
            canvas.create_oval(
                px - 4, py - 4, px + 4, py + 4,
                fill="#DDD", outline="", tags="pet"
            )
        canvas.create_text(
            cx + 40, cy - 40, text="♨",
            font=("Arial", 14), tags="pet"
        )

    elif mood == "sick":
        drop_y = cy - 35 + math.sin(tick / 10) * 2
        canvas.create_polygon(
            cx + 26, drop_y - 10,
            cx + 32, drop_y + 6,
            cx + 20, drop_y + 6,
            fill="#79CFFF", outline="", tags="pet"
        )
        if (tick // 14) % 2 == 0:
            canvas.create_text(
                cx - 38, cy - 48, text="✦", fill="#FFE082",
                font=("Arial", 10), tags="pet"
            )
            canvas.create_text(
                cx + 40, cy - 46, text="✦", fill="#FFE082",
                font=("Arial", 10), tags="pet"
            )


def _draw_pet(canvas, cx, cy, mood, tick, scale=1.0):
    _shadow(canvas, cx, cy)
    _body(canvas, cx, cy, mood, scale)
    _feet(canvas, cx, cy, mood, scale)
    _eyes(canvas, cx, cy, mood, tick, scale)
    _mouth(canvas, cx, cy, mood)
    _cheeks(canvas, cx, cy, mood)
    _mood_fx(canvas, cx, cy, mood, tick)


def _update_interactivity(canvas):
    """Check hover/click on canvas to drive scale and squish."""
    global _hover_scale, _squish

    try:
        mx = canvas.winfo_pointerx() - canvas.winfo_rootx()
        my = canvas.winfo_pointery() - canvas.winfo_rooty()
        in_bounds = 50 < mx < 170 and 50 < my < 170
    except Exception:
        in_bounds = False

    # Smooth hover scale
    target = 1.08 if in_bounds else 1.0
    _hover_scale += (target - _hover_scale) * 0.15

    # Decay squish
    _squish *= 0.85
    if _squish < 0.01:
        _squish = 0.0

    return _hover_scale * (1 - _squish), _squish


def _on_click(event):
    global _squish
    _squish = 0.25  # 25% squish on click


def _bind_click_once(canvas):
    if not getattr(canvas, "_droplet_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._droplet_click_bound = True


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bob = math.sin(tick / 18) * 2.5
    _draw_pet(canvas, CENTER_X, CENTER_Y + bob, "idle", tick, scale)
    _bind_click_once(canvas)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bounce = abs(math.sin(tick / 7)) * 10
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick, scale)
    _bind_click_once(canvas)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    shake = math.sin(tick * 0.9) * 3.5
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick, scale)
    _bind_click_once(canvas)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 22) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 4, "sick", tick, scale)
    _bind_click_once(canvas)
