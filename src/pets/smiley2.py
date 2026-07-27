"""smiley.py - 3D-ish smiley with hands, pupils, cheeks, and shadow."""

import math

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


def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, cx, cy):
    canvas.create_oval(
        cx - 44, cy + 38, cx + 44, cy + 52,
        fill="#1A1A1A", outline="", tags="pet"
    )


def _face(canvas, cx, cy, mood):
    fill = MOOD_FILL[mood]
    shade = MOOD_SHADE[mood]

    canvas.create_oval(
        cx - R, cy - R, cx + R, cy + R,
        fill=fill, outline="#3A3A3A", width=3, tags="pet"
    )
    canvas.create_arc(
        cx - R + 4, cy - R + 4, cx + R - 2, cy + R - 2,
        start=260, extent=120, style="arc", width=8,
        outline=shade, tags="pet"
    )
    canvas.create_oval(
        cx - 28, cy - 36, cx - 8, cy - 16,
        fill="white", outline="", tags="pet"
    )


def _hands(canvas, cx, cy, mood, tick):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 8
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 52, cy - 15 + wave,
                cx + side * 66, cy - 5 + wave,
                fill=fill, outline="#3A3A3A", width=2, tags="pet"
            )
    else:
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 50, cy + 5,
                cx + side * 62, cy + 20,
                fill=fill, outline="#3A3A3A", width=2, tags="pet"
            )


def _eyes(canvas, cx, cy, mood, tick):
    blink = (tick % 130) < 5

    if blink:
        for dx in (-16, 16):
            canvas.create_line(
                cx + dx - 7, cy - 4, cx + dx + 7, cy - 4,
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-16, 16):
            canvas.create_arc(
                cx + dx - 8, cy - 10, cx + dx + 8, cy + 4,
                start=0, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-16, 16):
            canvas.create_oval(
                cx + dx - 5, cy - 8, cx + dx + 5, cy + 6,
                fill="#1A1A1A", outline="", tags="pet"
            )
            slope = 1 if dx < 0 else -1
            canvas.create_line(
                cx + dx - 9, cy - 14, cx + dx + 7, cy - 10 + (3 * slope),
                width=3, fill="#1A1A1A", tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-16, 16):
            canvas.create_arc(
                cx + dx - 8, cy - 4, cx + dx + 8, cy + 8,
                start=180, extent=180, style="arc", width=3,
                outline="#1A1A1A", tags="pet"
            )
        return

    for dx in (-16, 16):
        canvas.create_oval(
            cx + dx - 7, cy - 10, cx + dx + 7, cy + 10,
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
            cx - 16, cy + 2, cx + 16, cy + 26,
            start=200, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
        canvas.create_oval(
            cx - 6, cy + 16, cx + 6, cy + 24,
            fill="#F4A6A0", outline="", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 12, cy + 16, cx + 12, cy + 12,
            width=3, fill="#1A1A1A", tags="pet"
        )
        canvas.create_line(
            cx - 8, cy + 14, cx + 8, cy + 14,
            width=2, fill="#DDD", tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            cx - 10, cy + 12, cx + 10, cy + 26,
            start=20, extent=140, style="arc", width=3,
            outline="#1A1A1A", tags="pet"
        )
        canvas.create_oval(
            cx - 4, cy + 18, cx + 4, cy + 28,
            fill="#E88B9B", outline="", tags="pet"
        )
    else:
        canvas.create_arc(
            cx - 8, cy + 8, cx + 8, cy + 20,
            start=200, extent=140, style="arc", width=2,
            outline="#1A1A1A", tags="pet"
        )


def _cheeks(canvas, cx, cy, mood):
    if mood in ("happy", "idle"):
        for dx in (-26, 26):
            canvas.create_oval(
                cx + dx - 7, cy + 4, cx + dx + 1, cy + 12,
                fill="#F4A6A0", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick):
    if mood == "happy":
        for i in range(3):
            sx = cx + math.sin(tick / 8 + i * 2) * 55
            sy = cy - 55 + i * 12
            canvas.create_text(
                sx, sy, text="✦", fill="#FFD95A",
                font=("Arial", 10, "bold"), tags="pet"
            )
    elif mood == "angry":
        canvas.create_line(
            cx - 30, cy - 28, cx - 20, cy - 32,
            width=2, fill="#D45A4A", tags="pet"
        )
        canvas.create_line(
            cx + 20, cy - 32, cx + 30, cy - 28,
            width=2, fill="#D45A4A", tags="pet"
        )
        canvas.create_text(
            cx + 45, cy - 42, text="mad",
            font=("Arial", 12, "bold"), fill="#D45A4A", tags="pet"
        )
        for side in (-1, 1):
            canvas.create_line(
                cx + side * 56, cy - 6, cx + side * 72, cy - 14,
                width=2, fill="#3A3A3A", tags="pet"
            )
            canvas.create_line(
                cx + side * 56, cy + 10, cx + side * 74, cy + 18,
                width=2, fill="#3A3A3A", tags="pet"
            )
    elif mood == "sick":
        canvas.create_polygon(
            cx + 28, cy - 26, cx + 34, cy - 12, cx + 22, cy - 12,
            fill="#79CFFF", outline="", tags="pet"
        )
        canvas.create_arc(
            cx - 16, cy - 30, cx + 16, cy - 8,
            start=0, extent=180, fill="#C8E6C9", outline="", tags="pet"
        )
        canvas.create_text(
            cx - 42, cy - 48, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )
        canvas.create_text(
            cx + 44, cy - 46, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )


def _draw_pet(canvas, cx, cy, mood, tick):
    _shadow(canvas, cx, cy)
    _hands(canvas, cx, cy, mood, tick)
    _face(canvas, cx, cy, mood)
    _eyes(canvas, cx, cy, mood, tick)
    _mouth(canvas, cx, cy, mood)
    _cheeks(canvas, cx, cy, mood)
    _mood_fx(canvas, cx, cy, mood, tick)


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    bob = math.sin(tick / 16) * 2.5
    _draw_pet(canvas, CENTER_X, CENTER_Y + bob, "idle", tick)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 10
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick * 0.85) * 4
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 20) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 5, "sick", tick)