"""robot.py - Retro cute robot with antenna, LED eyes, and exhaust vents."""

import math
import random

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2

BODY_W = 56
BODY_H = 62
HEAD_W = 48
HEAD_H = 40

MOOD_FILL = {
    "idle":  "#C0C8D4",
    "happy": "#A8D8EA",
    "angry": "#E8A8A8",
    "sick":  "#B8D4B8",
}

LED_COLORS = {
    "idle":  "#4ECDC4",
    "happy": "#44D644",
    "angry": "#FF4444",
    "sick":  "#FFAA00",
}

# ------------------------------------------------------------------
#  Interactivity state (shared across frames)
# ------------------------------------------------------------------
_hover_scale = 1.0
_squish = 0.0


def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, cx, cy, scale=1.0):
    canvas.create_oval(
        cx - 34 * scale, cy + 32 * scale,
        cx + 34 * scale, cy + 44 * scale,
        fill="#1A1A1A", outline="", tags="pet"
    )


def _rounded_rect(canvas, x1, y1, x2, y2, r, fill, outline, width, tags):
    """Draw a rounded rectangle using a smooth polygon on a tkinter canvas."""
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    canvas.create_polygon(pts, smooth=True, fill=fill, outline=outline,
                          width=width, tags=tags)


def _antenna(canvas, cx, cy, mood, tick, scale=1.0):
    canvas.create_line(cx, cy - 38 * scale, cx, cy - 52 * scale,
                       width=3, fill="#555", tags="pet")
    bulb_color = LED_COLORS[mood]
    canvas.create_oval(
        cx - 5 * scale, cy - 60 * scale, cx + 5 * scale, cy - 50 * scale,
        fill=bulb_color, outline="#333", width=2, tags="pet"
    )
    if mood == "sick" and (tick // 10) % 2 == 0:
        canvas.create_oval(
            cx - 5 * scale, cy - 60 * scale, cx + 5 * scale, cy - 50 * scale,
            fill="#555", outline="#333", width=2, tags="pet"
        )


def _head(canvas, cx, cy, mood, scale=1.0):
    fill = MOOD_FILL[mood]
    hx1 = cx - HEAD_W // 2 * scale
    hy1 = cy - 38 * scale
    hx2 = cx + HEAD_W // 2 * scale
    hy2 = cy - 2 * scale
    _rounded_rect(canvas, hx1, hy1, hx2, hy2, 8 * scale,
                  fill, "#444", 3, "pet")

    # Screen bezel
    _rounded_rect(canvas, cx - 18 * scale, cy - 30 * scale,
                  cx + 18 * scale, cy - 10 * scale, 4 * scale,
                  "#1A1A1A", "#666", 2, "pet")


def _track_led(canvas, led_cx, led_cy, max_off=2):
    """Robot LED eyes track the mouse with a subtle shift (random gaze)."""
    from src.pet_animations import track_mouse
    return track_mouse(canvas, led_cx, led_cy, max_offset=max_off)


def _eyes(canvas, cx, cy, mood, tick, scale=1.0):
    led = LED_COLORS[mood]

    # Random natural blink (LED flicker)
    blink = random.random() < 0.005 or (tick % 160 < 3 and random.random() < 0.3)

    if blink and mood not in ("angry", "sick"):
        # Brief LED off state
        for dx in (-10, 10):
            canvas.create_oval(
                cx + dx * scale - 3 * scale, cy - 24 * scale,
                cx + dx * scale + 3 * scale, cy - 18 * scale,
                fill="#333", outline="", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-10, 10):
            canvas.create_line(
                cx + dx * scale - 5 * scale, cy - 22 * scale,
                cx + dx * scale, cy - 28 * scale,
                cx + dx * scale + 5 * scale, cy - 22 * scale,
                width=3, fill=led, tags="pet"
            )
        return

    if mood == "angry":
        for side in (-1, 1):
            dx = side * 10
            canvas.create_line(
                cx + dx * scale - 5 * scale, cy - 26 * scale,
                cx + dx * scale + 5 * scale, cy - 22 * scale,
                width=3, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx * scale - 5 * scale, cy - 18 * scale,
                cx + dx * scale + 5 * scale, cy - 22 * scale,
                width=3, fill=led, tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-10, 10):
            canvas.create_line(
                cx + dx * scale - 6 * scale, cy - 24 * scale,
                cx + dx * scale - 2 * scale, cy - 20 * scale,
                width=2, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx * scale - 2 * scale, cy - 20 * scale,
                cx + dx * scale + 2 * scale, cy - 24 * scale,
                width=2, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx * scale + 2 * scale, cy - 24 * scale,
                cx + dx * scale + 6 * scale, cy - 20 * scale,
                width=2, fill=led, tags="pet"
            )
        return

    # Normal LED eyes — track mouse subtly (with random gaze pauses)
    for dx in (-10, 10):
        led_cx = cx + dx * scale
        led_cy = cy - 21 * scale
        px, py = _track_led(canvas, led_cx, led_cy, max_off=2 * scale)
        canvas.create_oval(
            px - 3 * scale, py - 3 * scale,
            px + 3 * scale, py + 3 * scale,
            fill=led, outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood, scale=1.0):
    if mood == "happy":
        canvas.create_arc(
            cx - 8 * scale, cy - 14 * scale,
            cx + 8 * scale, cy - 2 * scale,
            start=200, extent=140, style="arc", width=2,
            outline="#444", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 8 * scale, cy - 8 * scale,
            cx + 8 * scale, cy - 10 * scale,
            width=2, fill="#444", tags="pet"
        )
    elif mood == "sick":
        canvas.create_line(
            cx - 6 * scale, cy - 8 * scale,
            cx + 6 * scale, cy - 8 * scale,
            width=2, fill="#FFAA00", tags="pet"
        )
    else:
        canvas.create_rectangle(
            cx - 4 * scale, cy - 10 * scale,
            cx + 4 * scale, cy - 6 * scale,
            fill="#444", outline="", tags="pet"
        )


def _body(canvas, cx, cy, mood, scale=1.0):
    fill = MOOD_FILL[mood]
    bx1 = cx - BODY_W // 2 * scale
    by1 = cy - 2 * scale
    bx2 = cx + BODY_W // 2 * scale
    by2 = cy + 36 * scale
    _rounded_rect(canvas, bx1, by1, bx2, by2, 6 * scale,
                  fill, "#444", 3, "pet")

    # Chest panel
    _rounded_rect(canvas, cx - 16 * scale, cy + 4 * scale,
                  cx + 16 * scale, cy + 22 * scale, 3 * scale,
                  "#E8E8E8", "#888", 1, "pet")

    # Heartbeat line
    canvas.create_line(
        cx - 12 * scale, cy + 13 * scale, cx - 6 * scale, cy + 13 * scale,
        cx - 4 * scale, cy + 9 * scale, cx - 2 * scale, cy + 17 * scale,
        cx + 2 * scale, cy + 13 * scale, cx + 12 * scale, cy + 13 * scale,
        width=2, fill=LED_COLORS[mood], tags="pet"
    )


def _arms(canvas, cx, cy, mood, tick, scale=1.0):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 6
        for side in (-1, 1):
            x1 = cx + side * 34 * scale
            y1 = cy + 2 * scale + wave
            x2 = x1 + (12 * scale if side > 0 else -12 * scale)
            y2 = y1 + 14 * scale
            _rounded_rect(canvas, min(x1, x2), y1, max(x1, x2), y2, 3 * scale,
                          fill, "#444", 2, "pet")
    else:
        for side in (-1, 1):
            x1 = cx + side * 32 * scale
            y1 = cy + 8 * scale
            x2 = x1 + (12 * scale if side > 0 else -12 * scale)
            y2 = y1 + 14 * scale
            _rounded_rect(canvas, min(x1, x2), y1, max(x1, x2), y2, 3 * scale,
                          fill, "#444", 2, "pet")


def _exhaust(canvas, cx, cy, mood, tick, scale=1.0):
    if mood == "angry":
        for side in (-1, 1):
            px = cx + side * 20 * scale
            py = cy + 38 * scale - (tick % 16) * 0.6
            canvas.create_oval(
                px - 3 * scale, py - 3 * scale,
                px + 3 * scale, py + 3 * scale,
                fill="#CCC", outline="", tags="pet"
            )
    elif mood == "sick":
        if (tick // 8) % 2 == 0:
            canvas.create_oval(
                cx - 2 * scale, cy + 34 * scale,
                cx + 2 * scale, cy + 40 * scale,
                fill="#FFAA00", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick, scale=1.0):
    if mood == "happy":
        for i in range(2):
            sx = cx + math.sin(tick / 8 + i * 3) * 45 * scale
            sy = cy - 55 * scale + i * 14
            canvas.create_text(
                sx, sy, text="✦", fill="#44D644",
                font=("Arial", 10, "bold"), tags="pet"
            )

    elif mood == "angry":
        canvas.create_text(
            cx + 38 * scale, cy - 48 * scale, text="zap",
            font=("Arial", 12, "bold"), fill="#FF4444", tags="pet"
        )

    elif mood == "sick":
        canvas.create_text(
            cx + 36 * scale, cy - 48 * scale, text="fix",
            font=("Arial", 12, "bold"), fill="#FFAA00", tags="pet"
        )


def _draw_pet(canvas, cx, cy, mood, tick, scale=1.0):
    _shadow(canvas, cx, cy, scale)
    _exhaust(canvas, cx, cy, mood, tick, scale)
    _arms(canvas, cx, cy, mood, tick, scale)
    _body(canvas, cx, cy, mood, scale)
    _head(canvas, cx, cy, mood, scale)
    _antenna(canvas, cx, cy, mood, tick, scale)
    _eyes(canvas, cx, cy, mood, tick, scale)
    _mouth(canvas, cx, cy, mood, scale)
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
    if not getattr(canvas, "_robot_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._robot_click_bound = True


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    hover = math.sin(tick / 16) * 2
    _draw_pet(canvas, CENTER_X, CENTER_Y + hover, "idle", tick, scale)
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
    shake = math.sin(tick * 0.9) * 3.5
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick, scale)
    _bind_click_once(canvas)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 20) * 4
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 3, "sick", tick, scale)
    _bind_click_once(canvas)
