"""droplet.py - Glossy teardrop pet with depth, feet, and mood effects."""

import math

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


def _clear(canvas):
    canvas.delete("pet")


def _teardrop_points(cx, cy, w, h):
    """
    Full closed teardrop: pointed top, rounded bottom.
    Returns a flat list [x1,y1,x2,y2,...] for create_polygon.
    """
    pts = []
    steps = 48
    for i in range(steps):
        t = (i / steps) * 2 * math.pi
        # Parametric teardrop
        x = cx + math.sin(t) * (w / 2) * (1 - 0.4 * math.cos(t))
        y = cy - math.cos(t) * (h / 2)
        pts.extend([x, y])
    return pts


def _shadow(canvas, cx, cy):
    canvas.create_oval(
        cx - 36, cy + 38, cx + 36, cy + 50,
        fill="#1A1A1A", outline="", tags="pet"
    )


def _body(canvas, cx, cy, mood):
    fill = MOOD_FILL[mood]
    glow = MOOD_GLOW[mood]

    # Main teardrop
    pts = _teardrop_points(cx, cy, BODY_W, BODY_H)
    canvas.create_polygon(
        pts, fill=fill, outline="#3A3A3A", width=3,
        smooth=True, tags="pet"
    )

    # Inner glow (depth)
    inner_pts = _teardrop_points(cx, cy + 4, BODY_W - 18, BODY_H - 18)
    canvas.create_polygon(
        inner_pts, fill=glow, outline="", smooth=True, tags="pet"
    )

    # Glossy highlight (upper-left)
    canvas.create_oval(
        cx - 18, cy - 28, cx + 2, cy - 8,
        fill="white", outline="", tags="pet"
    )
    canvas.create_oval(
        cx - 10, cy - 24, cx - 2, cy - 16,
        fill="#FFFFFF", outline="", tags="pet"
    )


def _feet(canvas, cx, cy, mood):
    fill = MOOD_FILL[mood]
    for dx in (-18, 18):
        canvas.create_oval(
            cx + dx - 10, cy + 32, cx + dx + 10, cy + 46,
            fill=fill, outline="#3A3A3A", width=2, tags="pet"
        )


def _eyes(canvas, cx, cy, mood, tick):
    blink = (tick % 140) < 5

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

    # Normal
    for dx in (-14, 14):
        canvas.create_oval(
            cx + dx - 6, cy - 8, cx + dx + 6, cy + 8,
            fill="white", outline="#3A3A3A", width=1, tags="pet"
        )
        canvas.create_oval(
            cx + dx - 3, cy - 4, cx + dx + 1, cy + 2,
            fill="#1A1A1A", outline="", tags="pet"
        )
        canvas.create_oval(
            cx + dx - 2, cy - 6, cx + dx, cy - 4,
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


def _draw_pet(canvas, cx, cy, mood, tick):
    _shadow(canvas, cx, cy)
    _body(canvas, cx, cy, mood)
    _feet(canvas, cx, cy, mood)
    _eyes(canvas, cx, cy, mood, tick)
    _mouth(canvas, cx, cy, mood)
    _cheeks(canvas, cx, cy, mood)
    _mood_fx(canvas, cx, cy, mood, tick)


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    bob = math.sin(tick / 18) * 2.5
    _draw_pet(canvas, CENTER_X, CENTER_Y + bob, "idle", tick)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 7)) * 10
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick * 0.9) * 3.5
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 22) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 4, "sick", tick)