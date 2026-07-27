"""cat.py - Improved procedural cat pet. Drop-in replacement for RoastBot."""

import math

CANVAS_SIZE = 220
CENTER_X = CANVAS_SIZE // 2
CENTER_Y = CANVAS_SIZE // 2

COLORS = {
    "idle": "#E8C994",
    "happy": "#F2D49B",
    "angry": "#D47C69",
    "sick": "#B8B89E",
    "outline": "#4A3B2A",
    "ear_inner": "#F3AFC0",
    "eye": "#1C1A19",
    "nose": "#E88B9B",
    "cheek": "#F2A7A7",
    "shadow": "#111111",
    "belly": "#F7E6C9",
    "stripe": "#C49A6C",
    "pale": "#C8E6C9",
    "sweat": "#79CFFF",
}


# --------------------------------------------------------------------------- #
#  Low-level helpers
# --------------------------------------------------------------------------- #
def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, x, y):
    canvas.create_oval(
        x - 45, y + 48, x + 45, y + 60,
        fill=COLORS["shadow"], outline="", tags="pet"
    )


def _tail(canvas, x, y, tick, mood):
    """Multi-segment tail for fluid, tapering motion."""
    segments = 6
    length = 70
    start_x, start_y = x + 25, y + 25

    if mood == "happy":
        freq, amp = 0.15, 15
    elif mood == "angry":
        freq, amp = 0.4, 22
    else:
        freq, amp = 0.08, 8

    points = []
    for i in range(segments + 1):
        t = i / segments
        px = start_x + t * length
        wave = math.sin(tick * freq - t * 3) * amp * (t ** 0.5)
        py = start_y + wave + t * 10
        points.extend([px, py])

    for i in range(len(points) // 2 - 1):
        x1, y1 = points[i * 2], points[i * 2 + 1]
        x2, y2 = points[(i + 1) * 2], points[(i + 1) * 2 + 1]
        width = max(2, 10 - i)
        canvas.create_line(
            x1, y1, x2, y2,
            width=width,
            fill=COLORS["outline"],
            capstyle="round",
            tags="pet",
        )


def _body(canvas, x, y, fill):
    canvas.create_oval(
        x - 38, y + 12, x + 38, y + 75,
        fill=fill, outline=COLORS["outline"], width=3, tags="pet"
    )
    # Belly patch
    canvas.create_oval(
        x - 18, y + 30, x + 18, y + 65,
        fill=COLORS["belly"], outline="", tags="pet"
    )


def _ears(canvas, x, y, fill):
    for side in (-1, 1):
        # Outer ear
        canvas.create_polygon(
            x + side * 20, y - 22,
            x + side * 50, y - 72,
            x + side * 10, y - 52,
            fill=fill, outline=COLORS["outline"], width=3, tags="pet"
        )
        # Inner ear
        canvas.create_polygon(
            x + side * 22, y - 37,
            x + side * 40, y - 62,
            x + side * 18, y - 50,
            fill=COLORS["ear_inner"], outline="", tags="pet"
        )


def _head(canvas, x, y, fill):
    canvas.create_oval(
        x - 46, y - 42, x + 46, y + 42,
        fill=fill, outline=COLORS["outline"], width=3, tags="pet"
    )


def _cheeks(canvas, x, y):
    for dx in (-40, 40):
        mult = 1 if dx < 0 else -1
        canvas.create_polygon(
            x + dx, y + 5,
            x + dx + mult * 10, y + 15,
            x + dx, y + 25,
            x + dx + mult * 14, y + 18,
            fill="#F7D9B8", outline="", tags="pet"
        )


def _whiskers(canvas, x, y):
    for side in (-1, 1):
        for i in (-1, 0, 1):
            yy = y + i * 6 + 5
            canvas.create_line(
                x + side * 20, yy,
                x + side * 55, yy + side * 4 + i * 2,
                fill="#555", width=2, tags="pet"
            )


def _nose(canvas, x, y):
    canvas.create_polygon(
        x, y + 12, x - 5, y + 20, x + 5, y + 20,
        fill=COLORS["nose"], outline="", tags="pet"
    )


def _muzzle(canvas, x, y):
    canvas.create_oval(
        x - 18, y + 8, x + 18, y + 32,
        fill="#F8EBD8", outline="", tags="pet"
    )
    _nose(canvas, x, y)
    canvas.create_line(x, y + 20, x, y + 26, width=2, tags="pet")


def _eyes(canvas, x, y, mood, tick):
    blink = (tick % 150) < 5

    if blink:
        for dx in (-18, 18):
            canvas.create_line(
                x + dx - 7, y - 2, x + dx + 7, y - 2,
                width=3, tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-18, 18):
            canvas.create_arc(
                x + dx - 8, y - 8, x + dx + 8, y + 6,
                start=0, extent=180, style="arc", width=3, tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-18, 18):
            canvas.create_oval(
                x + dx - 6, y - 8, x + dx + 6, y + 8,
                fill=COLORS["eye"], outline="", tags="pet"
            )
            if dx < 0:
                canvas.create_line(
                    x + dx - 10, y - 14, x + dx + 8, y - 8,
                    width=3, tags="pet"
                )
            else:
                canvas.create_line(
                    x + dx + 10, y - 14, x + dx - 8, y - 8,
                    width=3, tags="pet"
                )
        return

    if mood == "sick":
        for dx in (-18, 18):
            canvas.create_arc(
                x + dx - 8, y - 3, x + dx + 8, y + 8,
                start=180, extent=180, style="arc", width=3, tags="pet"
            )
        return

    # Normal eyes
    for dx in (-18, 18):
        canvas.create_oval(
            x + dx - 7, y - 10, x + dx + 7, y + 10,
            fill=COLORS["eye"], outline="", tags="pet"
        )
        # Eye shine
        canvas.create_oval(
            x + dx - 4, y - 6, x + dx - 1, y - 3,
            fill="white", outline="", tags="pet"
        )
        canvas.create_oval(
            x + dx + 1, y + 1, x + dx + 3, y + 3,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, x, y, mood):
    if mood == "happy":
        canvas.create_arc(
            x - 14, y + 18, x + 14, y + 36,
            start=200, extent=140, style="arc", width=3, tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            x - 12, y + 26, x + 12, y + 22,
            width=3, tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            x - 10, y + 22, x + 10, y + 36,
            start=20, extent=140, style="arc", width=3, tags="pet"
        )
    else:
        canvas.create_arc(
            x - 9, y + 22, x + 9, y + 32,
            start=200, extent=140, style="arc", width=2, tags="pet"
        )


def _face(canvas, x, y, mood, tick):
    _eyes(canvas, x, y, mood, tick)
    _muzzle(canvas, x, y)
    _mouth(canvas, x, y, mood)
    _whiskers(canvas, x, y)

    if mood == "happy":
        for dx in (-25, 25):
            canvas.create_oval(
                x + dx - 6, y + 10, x + dx + 6, y + 20,
                fill=COLORS["cheek"], outline="", tags="pet"
            )


def _forehead(canvas, x, y):
    # Hair tuft
    canvas.create_line(
        x, y - 42, x - 5, y - 58, x + 2, y - 53, x + 8, y - 63,
        smooth=True, width=3, fill=COLORS["outline"], tags="pet"
    )
    # Stripes
    for dx in (-15, 0, 15):
        canvas.create_arc(
            x + dx - 6, y - 32, x + dx + 6, y - 8,
            start=180, extent=180, style="arc", width=2,
            outline=COLORS["stripe"], tags="pet"
        )


def _paws(canvas, x, y, fill):
    for dx in (-22, 22):
        canvas.create_oval(
            x + dx - 13, y + 52, x + dx + 13, y + 77,
            fill=fill, outline=COLORS["outline"], width=2, tags="pet"
        )
        canvas.create_line(
            x + dx, y + 64, x + dx, y + 74,
            width=1, tags="pet"
        )


def _draw_cat(canvas, x, y, mood, tick):
    fill = COLORS[mood]

    _shadow(canvas, x, y)
    _tail(canvas, x, y, tick, mood)   # behind body
    _body(canvas, x, y, fill)
    _ears(canvas, x, y, fill)
    _head(canvas, x, y, fill)
    _cheeks(canvas, x, y)
    _forehead(canvas, x, y)
    _paws(canvas, x, y, fill)
    _face(canvas, x, y, mood, tick)


# --------------------------------------------------------------------------- #
#  Public API (required by pet_animations.py)
# --------------------------------------------------------------------------- #
def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    bob = math.sin(tick / 20) * 2
    _draw_cat(canvas, CENTER_X, CENTER_Y + bob, "idle", tick)

    # Occasional ear twitch
    if tick % 140 < 6:
        canvas.create_line(
            CENTER_X - 34, CENTER_Y - 62,
            CENTER_X - 42, CENTER_Y - 74,
            width=2, fill=COLORS["outline"], tags="pet"
        )


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    bounce = abs(math.sin(tick / 8)) * 6
    _draw_cat(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick)

    # Sparkles
    for i in range(3):
        sx = CENTER_X + math.sin(tick / 8 + i * 2) * 50
        sy = CENTER_Y - 60 + i * 12
        canvas.create_text(
            sx, sy, text="✦", fill="#FFD95A",
            font=("Arial", 10, "bold"), tags="pet"
        )

    if (tick // 20) % 4 == 0:
        canvas.create_text(
            CENTER_X + 50, CENTER_Y - 55, text="♥",
            fill="#FF6B8A", font=("Arial", 11, "bold"), tags="pet"
        )


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    shake = math.sin(tick * 0.8) * 3
    x = CENTER_X + shake
    y = CENTER_Y

    _draw_cat(canvas, x, y, "angry", tick)

    # Flattened ears
    canvas.create_line(
        x - 34, y - 52, x - 48, y - 42,
        width=4, fill=COLORS["outline"], tags="pet"
    )
    canvas.create_line(
        x + 34, y - 52, x + 48, y - 42,
        width=4, fill=COLORS["outline"], tags="pet"
    )

    # Puff mark
    canvas.create_text(
        x + 50, y - 45, text="💢",
        font=("Arial", 16, "bold"), tags="pet"
    )

    # Motion lines
    for side in (-1, 1):
        canvas.create_line(
            x + side * 55, y - 8, x + side * 70, y - 15,
            width=2, fill=COLORS["outline"], tags="pet"
        )
        canvas.create_line(
            x + side * 55, y + 10, x + side * 72, y + 18,
            width=2, fill=COLORS["outline"], tags="pet"
        )


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    sway = math.sin(tick / 25) * 4
    x = CENTER_X + sway
    y = CENTER_Y + 3

    _draw_cat(canvas, x, y, "sick", tick)

    # Sweat drop
    canvas.create_polygon(
        x + 30, y - 28, x + 37, y - 12, x + 24, y - 12,
        fill=COLORS["sweat"], outline="", tags="pet"
    )

    # Pale forehead
    canvas.create_arc(
        x - 18, y - 32, x + 18, y - 8,
        start=0, extent=180, fill=COLORS["pale"], outline="", tags="pet"
    )

    # Dizzy stars
    if (tick // 12) % 2 == 0:
        canvas.create_text(
            x - 40, y - 50, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )
        canvas.create_text(
            x + 42, y - 48, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )

    # Wobble lines
    canvas.create_line(
        x - 28, y + 55, x - 32, y + 65,
        width=2, fill=COLORS["outline"], tags="pet"
    )
    canvas.create_line(
        x + 28, y + 55, x + 32, y + 65,
        width=2, fill=COLORS["outline"], tags="pet"
    )