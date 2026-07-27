"""ghost.py - Cute floating ghost with wavy hem, big eyes, and tiny arms."""

import math

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


def _clear(canvas):
    canvas.delete("pet")


def _ghost_body(canvas, cx, cy, mood, tick):
    fill = MOOD_FILL[mood]
    outline = "#555555" if mood != "angry" else "#AA4444"

    # Build full outline as a single polygon
    pts = []

    # Top dome: left to right (180° to 0°)
    for i in range(21):
        a = math.radians(180 - i * 9)  # 180 down to 0
        px = cx + (GHOST_W / 2) * math.cos(a)
        py = cy - 10 - (GHOST_W / 2) * math.sin(a)
        pts.extend([px, py])

    # Right side down to bottom-right
    pts.extend([cx + GHOST_W / 2, cy + 10])

    # Wavy bottom edge: right to left
    waves = 5
    for i in range(waves + 1):
        t = i / waves
        px = (cx + GHOST_W / 2) - GHOST_W * t
        py = cy + GHOST_H / 2 + math.sin(tick / 8 + t * 4) * 3
        pts.extend([px, py])

    # Left side up to close
    pts.extend([cx - GHOST_W / 2, cy + 10])

    canvas.create_polygon(
        pts, fill=fill, outline=outline, width=3,
        smooth=True, tags="pet"
    )


def _arms(canvas, cx, cy, mood, tick):
    fill = MOOD_FILL[mood]
    if mood == "happy":
        wave = math.sin(tick / 6) * 8
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 42, cy - 15 + wave,
                cx + side * 54, cy - 5 + wave,
                fill=fill, outline="#555", width=2, tags="pet"
            )
    else:
        for side in (-1, 1):
            canvas.create_oval(
                cx + side * 40, cy + 5,
                cx + side * 52, cy + 18,
                fill=fill, outline="#555", width=2, tags="pet"
            )


def _eyes(canvas, cx, cy, mood, tick):
    blink = (tick % 120) < 4

    if blink:
        for dx in (-14, 14):
            canvas.create_line(
                cx + dx - 6, cy - 8, cx + dx + 6, cy - 8,
                width=3, fill="#222", tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx - 8, cy - 14, cx + dx + 8, cy - 2,
                start=0, extent=180, style="arc", width=3,
                outline="#222", tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-14, 14):
            canvas.create_oval(
                cx + dx - 5, cy - 12, cx + dx + 5, cy - 2,
                fill="#222", outline="", tags="pet"
            )
            slope = 1 if dx < 0 else -1
            canvas.create_line(
                cx + dx - 8, cy - 18, cx + dx + 6, cy - 14 + (3 * slope),
                width=3, fill="#222", tags="pet"
            )
        return

    if mood == "sick":
        for dx in (-14, 14):
            canvas.create_arc(
                cx + dx - 8, cy - 10, cx + dx + 8, cy,
                start=180, extent=180, style="arc", width=3,
                outline="#222", tags="pet"
            )
        return

    # Normal big cute eyes
    for dx in (-14, 14):
        canvas.create_oval(
            cx + dx - 8, cy - 14, cx + dx + 8, cy + 2,
            fill="white", outline="#222", width=2, tags="pet"
        )
        canvas.create_oval(
            cx + dx - 3, cy - 8, cx + dx + 3, cy - 2,
            fill="#222", outline="", tags="pet"
        )
        canvas.create_oval(
            cx + dx - 2, cy - 6, cx + dx, cy - 4,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, cx, cy, mood):
    if mood == "happy":
        canvas.create_arc(
            cx - 10, cy + 2, cx + 10, cy + 18,
            start=200, extent=140, style="arc", width=3,
            outline="#222", tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            cx - 10, cy + 10, cx + 10, cy + 6,
            width=3, fill="#222", tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            cx - 8, cy + 6, cx + 8, cy + 18,
            start=20, extent=140, style="arc", width=3,
            outline="#222", tags="pet"
        )
    else:
        canvas.create_oval(
            cx - 3, cy + 6, cx + 3, cy + 12,
            fill="#222", outline="", tags="pet"
        )


def _cheeks(canvas, cx, cy, mood):
    if mood in ("happy", "idle"):
        for dx in (-22, 22):
            canvas.create_oval(
                cx + dx - 6, cy - 2, cx + dx + 2, cy + 6,
                fill="#FFB8C9", outline="", tags="pet"
            )


def _mood_fx(canvas, cx, cy, mood, tick):
    if mood == "happy":
        for i in range(3):
            sx = cx + math.sin(tick / 8 + i * 2) * 50
            sy = cy - 50 + i * 12
            canvas.create_text(
                sx, sy, text="✦", fill="#B8E0FF",
                font=("Arial", 10, "bold"), tags="pet"
            )

    elif mood == "angry":
        canvas.create_text(
            cx + 40, cy - 38, text="boo",
            font=("Arial", 12, "bold"), fill="#AA4444", tags="pet"
        )
        for side in (-1, 1):
            canvas.create_line(
                cx + side * 50, cy - 4, cx + side * 64, cy - 10,
                width=2, fill="#AA4444", tags="pet"
            )

    elif mood == "sick":
        canvas.create_polygon(
            cx + 24, cy - 22, cx + 30, cy - 8, cx + 18, cy - 8,
            fill="#79CFFF", outline="", tags="pet"
        )
        if (tick // 14) % 2 == 0:
            canvas.create_text(
                cx - 36, cy - 42, text="✦", fill="#C8E6C9",
                font=("Arial", 10), tags="pet"
            )


def _draw_pet(canvas, cx, cy, mood, tick):
    _arms(canvas, cx, cy, mood, tick)
    _ghost_body(canvas, cx, cy, mood, tick)
    _eyes(canvas, cx, cy, mood, tick)
    _mouth(canvas, cx, cy, mood)
    _cheeks(canvas, cx, cy, mood)
    _mood_fx(canvas, cx, cy, mood, tick)


def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    hover = math.sin(tick / 18) * 3
    _draw_pet(canvas, CENTER_X, CENTER_Y + hover, "idle", tick)


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 6)) * 12
    _draw_pet(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick)


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick * 0.9) * 4
    _draw_pet(canvas, CENTER_X + shake, CENTER_Y, "angry", tick)


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 22) * 5
    _draw_pet(canvas, CENTER_X + sway, CENTER_Y + 4, "sick", tick)