"""robot.py - Retro cute robot with antenna, LED eyes, and exhaust vents."""

import math

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


def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, cx, cy):
    canvas.create_oval(
        cx - 34, cy + 32, cx + 34, cy + 44,
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


def _antenna(canvas, cx, cy, mood, tick):
    canvas.create_line(cx, cy - 38, cx, cy - 52, width=3, fill="#555", tags="pet")
    bulb_color = LED_COLORS[mood]
    canvas.create_oval(
        cx - 5, cy - 60, cx + 5, cy - 50,
        fill=bulb_color, outline="#333", width=2, tags="pet"
    )
    if mood == "sick" and (tick // 10) % 2 == 0:
        canvas.create_oval(
            cx - 5, cy - 60, cx + 5, cy - 50,
            fill="#555", outline="#333", width=2, tags="pet"
        )


def _head(canvas, cx, cy, mood):
    fill = MOOD_FILL[mood]
    hx1, hy1 = cx - HEAD_W // 2, cy - 38
    hx2, hy2 = cx + HEAD_W // 2, cy - 2
    _rounded_rect(canvas, hx1, hy1, hx2, hy2, 8,
                  fill, "#444", 3, "pet")

    # Screen bezel
    _rounded_rect(canvas, cx - 18, cy - 30, cx + 18, cy - 10, 4,
                  "#1A1A1A", "#666", 2, "pet")


def _eyes(canvas, cx, cy, mood, tick):
    led = LED_COLORS[mood]

    if mood == "happy":
        for dx in (-10, 10):
            canvas.create_line(
                cx + dx - 5, cy - 22, cx + dx, cy - 28, cx + dx + 5, cy - 22,
                width=3, fill=led, tags="pet"
            )
        return

    if mood == "angry":
        for side in (-1, 1):
            dx = side * 10
            canvas.create_line(
                cx + dx - 5, cy - 26, cx + dx + 5, cy - 22,
                width=3, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx - 5, cy - 18, cx + dx + 5, cy - 22,
                width=3, fill=led, tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-10, 10):
            canvas.create_line(
                cx + dx - 6, cy - 24, cx + dx - 2, cy - 20,
                width=2, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx - 2, cy - 20, cx + dx + 2, cy - 24,
                width=2, fill=led, tags="pet"
            )
            canvas.create_line(
                cx + dx + 2, cy - 24, cx + dx + 6, cy - 20,
                width=2, fill=led, tags="pet"
            )
        return

    for dx in (-10, 10):
        canvas.create_oval(
            cx + dx - 3, cy - 24, cx + dx + 3, cy - 18,
            fill=led, outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood):
    if mood == "happy":
        canvas.create_arc(
            cx - 8, cy - 14, cx + 8, cy - 2,
            start=200, extent=140, style="arc", width=2,
            outline="#444", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 8, cy - 8, cx + 8, cy - 10,
            width=2, fill="#444", tags="pet"
        )
    elif mood == "sick":
        canvas.create_line(
            cx - 6, cy - 8, cx + 6, cy - 8,
            width=2, fill="#FFAA00", tags="pet"
        )
    else:
        canvas.create_rectangle(
            cx - 4, cy - 10, cx + 4, cy - 6,
            fill="#444", outline="", tags="pet"
        )


def _body(canvas, cx, cy, mood):
    fill = MOOD_FILL[mood]
    bx1, by1 = cx - BODY_W // 2, cy - 2
    bx2, by2 = cx + BODY_W // 2, cy + 36
    _rounded_rect(canvas, bx1, by1, bx2, by2, 6,
                  fill, "#444", 3, "pet")

    # Chest panel
    _rounded_rect(canvas, cx - 16, cy + 4, cx + 16, cy + 22, 3,
                  "#E8E8E8", "#888", 1, "pet")

    # Heartbeat line
    canvas.create_line(
        cx - 12, cy + 13, cx - 6, cy + 13,
        cx - 4, cy + 9, cx - 2, cy + 17,
        cx + 2, cy + 13, cx + 12, cy + 13,
        width=2, fill=LED_COLORS[mood], tags="pet"
    )


def _arms(canvas, cx, cy, mood, tick):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 6
        for side in (-1, 1):
            x1 = cx + side * 34
            y1 = cy + 2 + wave
            x2 = x1 + (12 if side > 0 else -12)
            y2 = y1 + 14
            _rounded_rect(canvas, min(x1, x2), y1, max(x1, x2), y2, 3,
                          fill, "#444", 2, "pet")
    else:
        for side in (-1, 1):
            x1 = cx + side * 32
            y1 = cy + 8
            x2 = x1 + (12 if side > 0 else -12)
            y2 = y1 + 14
            _rounded_rect(canvas, min(x1, x2), y1, max(x1, x2), y2, 3,
                          fill, "#444", 2, "pet")


def _exhaust(canvas, cx, cy, mood, tick):
    if mood == "angry":
        for side in (-1, 1):
            px = cx + side * 20
            py = cy + 38 - (tick % 16) * 0.6
            canvas.create_oval(
                px - 3, py - 3, px + 3, py + 3,
                fill="#CCC", outline="", tags="pet"
            )
    elif mood == "sick":
        if (tick // 8) % 2 == 0:
            canvas.create_oval(
                cx - 2, cy + 34, cx + 2, cy + 40,
                fill="#FFAA00", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick):
    if mood == "happy":
        for i in range(2):
            sx = cx + math.sin(tick / 8 + i * 3) * 45
            sy = cy - 55 + i * 14
            canvas.create_text(
                sx, sy, text="✦", fill="#44D644",
                font=("Arial", 10, "bold"), tags="pet"
            )

    elif mood == "angry":
        canvas.create_text(
            cx + 38, cy - 48, text="zap",
            font=("Arial", 12, "bold"), fill="#FF4444", tags="pet"
        )

    elif mood == "sick":
        canvas.create_text(
            cx + 36, cy - 48, text="fix",
            font=("Arial", 12, "bold"), fill="#FFAA00", tags="pet"
        )


def _draw_pet(canvas, cx, cy, mood, tick):
    _shadow(canvas, cx, cy)
    _exhaust(canvas, cx, cy, mood, tick)
    _arms(canvas, cx, cy, mood, tick)
    _body(canvas, cx, cy, mood)
    _head(canvas, cx, cy, mood)
    _antenna(canvas, cx, cy, mood, tick)
    _eyes(canvas, cx, cy, mood, tick)
    _mouth(canvas, cx, cy, mood)
    _mood_fx(canvas, cx, cy, mood, tick)


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    hover = math.sin(tick / 16) * 2
    _draw_pet(canvas, CENTER_X, CENTER_Y + hover, "idle", tick)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick * 0.9) * 3.5
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 20) * 4
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 3, "sick", tick)