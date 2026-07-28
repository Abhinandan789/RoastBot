"""cat.py - Improved procedural cat pet. Drop-in replacement for RoastBot."""

import math
import random

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

# ------------------------------------------------------------------
#  Interactivity state (shared across frames)
# ------------------------------------------------------------------
_hover_scale = 1.0
_squish = 0.0


# --------------------------------------------------------------------------- #
#  Low-level helpers
# --------------------------------------------------------------------------- #
def _clear(canvas):
    canvas.delete("pet")


def _shadow(canvas, x, y, scale=1.0):
    canvas.create_oval(
        x - 45 * scale, y + 48 * scale,
        x + 45 * scale, y + 60 * scale,
        fill=COLORS["shadow"], outline="", tags="pet"
    )


def _tail(canvas, x, y, tick, mood, scale=1.0):
    """Multi-segment tail for fluid, tapering motion."""
    segments = 6
    length = 70 * scale
    start_x, start_y = x + 25 * scale, y + 25 * scale

    if mood == "happy":
        freq, amp = 0.15, 15 * scale
    elif mood == "angry":
        freq, amp = 0.4, 22 * scale
    else:
        freq, amp = 0.08, 8 * scale

    points = []
    for i in range(segments + 1):
        t = i / segments
        px = start_x + t * length
        wave = math.sin(tick * freq - t * 3) * amp * (t ** 0.5)
        py = start_y + wave + t * 10 * scale
        points.extend([px, py])

    for i in range(len(points) // 2 - 1):
        x1, y1 = points[i * 2], points[i * 2 + 1]
        x2, y2 = points[(i + 1) * 2], points[(i + 1) * 2 + 1]
        width = max(2, int(10 * scale - i))
        canvas.create_line(
            x1, y1, x2, y2,
            width=width,
            fill=COLORS["outline"],
            capstyle="round",
            tags="pet",
        )


def _body(canvas, x, y, fill, scale=1.0):
    canvas.create_oval(
        x - 38 * scale, y + 12 * scale,
        x + 38 * scale, y + 75 * scale,
        fill=fill, outline=COLORS["outline"], width=3, tags="pet"
    )
    # Belly patch
    canvas.create_oval(
        x - 18 * scale, y + 30 * scale,
        x + 18 * scale, y + 65 * scale,
        fill=COLORS["belly"], outline="", tags="pet"
    )


def _ears(canvas, x, y, fill, scale=1.0):
    for side in (-1, 1):
        # Outer ear
        canvas.create_polygon(
            x + side * 20 * scale, y - 22 * scale,
            x + side * 50 * scale, y - 72 * scale,
            x + side * 10 * scale, y - 52 * scale,
            fill=fill, outline=COLORS["outline"], width=3, tags="pet"
        )
        # Inner ear
        canvas.create_polygon(
            x + side * 22 * scale, y - 37 * scale,
            x + side * 40 * scale, y - 62 * scale,
            x + side * 18 * scale, y - 50 * scale,
            fill=COLORS["ear_inner"], outline="", tags="pet"
        )


def _head(canvas, x, y, fill, scale=1.0):
    canvas.create_oval(
        x - 46 * scale, y - 42 * scale,
        x + 46 * scale, y + 42 * scale,
        fill=fill, outline=COLORS["outline"], width=3, tags="pet"
    )


def _cheeks(canvas, x, y, scale=1.0):
    for dx in (-40, 40):
        mult = 1 if dx < 0 else -1
        canvas.create_polygon(
            x + dx * scale, y + 5 * scale,
            x + dx * scale + mult * 10 * scale, y + 15 * scale,
            x + dx * scale, y + 25 * scale,
            x + dx * scale + mult * 14 * scale, y + 18 * scale,
            fill="#F7D9B8", outline="", tags="pet"
        )


def _whiskers(canvas, x, y, scale=1.0):
    for side in (-1, 1):
        for i in (-1, 0, 1):
            yy = y + i * 6 * scale + 5 * scale
            canvas.create_line(
                x + side * 20 * scale, yy,
                x + side * 55 * scale, yy + side * 4 * scale + i * 2 * scale,
                fill="#555", width=2, tags="pet"
            )


def _nose(canvas, x, y, scale=1.0):
    canvas.create_polygon(
        x, y + 12 * scale,
        x - 5 * scale, y + 20 * scale,
        x + 5 * scale, y + 20 * scale,
        fill=COLORS["nose"], outline="", tags="pet"
    )


def _muzzle(canvas, x, y, scale=1.0):
    canvas.create_oval(
        x - 18 * scale, y + 8 * scale,
        x + 18 * scale, y + 32 * scale,
        fill="#F8EBD8", outline="", tags="pet"
    )
    _nose(canvas, x, y, scale)
    canvas.create_line(x, y + 20 * scale, x, y + 26 * scale, width=2, tags="pet")


def _track_pupil(canvas, eye_cx, eye_cy, max_off=4):
    """Track mouse with random gaze: follow for a bit, then rest at center."""
    from src.pet_animations import track_mouse
    return track_mouse(canvas, eye_cx, eye_cy, max_offset=max_off)


def _eyes(canvas, x, y, mood, tick, scale=1.0):
    # Random natural blink
    blink = random.random() < 0.005 or (tick % 150 < 5 and random.random() < 0.3)

    if blink:
        for dx in (-18, 18):
            canvas.create_line(
                x + dx * scale - 7 * scale, y - 2 * scale,
                x + dx * scale + 7 * scale, y - 2 * scale,
                width=3, tags="pet"
            )
        return

    if mood == "happy":
        for dx in (-18, 18):
            canvas.create_arc(
                x + dx * scale - 8 * scale, y - 8 * scale,
                x + dx * scale + 8 * scale, y + 6 * scale,
                start=0, extent=180, style="arc", width=3, tags="pet"
            )
        return

    if mood == "angry":
        for dx in (-18, 18):
            canvas.create_oval(
                x + dx * scale - 6 * scale, y - 8 * scale,
                x + dx * scale + 6 * scale, y + 8 * scale,
                fill=COLORS["eye"], outline="", tags="pet"
            )
            if dx < 0:
                canvas.create_line(
                    x + dx * scale - 10 * scale, y - 14 * scale,
                    x + dx * scale + 8 * scale, y - 8 * scale,
                    width=3, tags="pet"
                )
            else:
                canvas.create_line(
                    x + dx * scale + 10 * scale, y - 14 * scale,
                    x + dx * scale - 8 * scale, y - 8 * scale,
                    width=3, tags="pet"
                )
        return

    if mood == "sick":
        for dx in (-18, 18):
            canvas.create_arc(
                x + dx * scale - 8 * scale, y - 3 * scale,
                x + dx * scale + 8 * scale, y + 8 * scale,
                start=180, extent=180, style="arc", width=3, tags="pet"
            )
        return

    # Normal eyes — with mouse-tracking pupil slit + shifting shine (random gaze)
    for dx in (-18, 18):
        ex = x + dx * scale
        ey = y
        # Eye shape
        canvas.create_oval(
            ex - 7 * scale, ey - 10 * scale,
            ex + 7 * scale, ey + 10 * scale,
            fill=COLORS["eye"], outline="", tags="pet"
        )
        # Vertical pupil slit that tracks mouse (with random gaze pauses)
        px, py = _track_pupil(canvas, ex, ey, max_off=3 * scale)
        canvas.create_oval(
            px - 1.5 * scale, py - 5 * scale,
            px + 1.5 * scale, py + 5 * scale,
            fill="#0A0A0A", outline="", tags="pet"
        )
        # Eye shine shifts slightly opposite to pupil (light source effect)
        shine_dx = (ex - px) * 0.4
        shine_dy = (ey - py) * 0.4
        canvas.create_oval(
            ex - 4 * scale + shine_dx, ey - 6 * scale + shine_dy,
            ex - 1 * scale + shine_dx, ey - 3 * scale + shine_dy,
            fill="white", outline="", tags="pet"
        )
        canvas.create_oval(
            ex + 1 * scale + shine_dx, ey + 1 * scale + shine_dy,
            ex + 3 * scale + shine_dx, ey + 3 * scale + shine_dy,
            fill="white", outline="", tags="pet"
        )


def _mouth(canvas, x, y, mood, scale=1.0):
    if mood == "happy":
        canvas.create_arc(
            x - 14 * scale, y + 18 * scale,
            x + 14 * scale, y + 36 * scale,
            start=200, extent=140, style="arc", width=3, tags="pet"
        )
    elif mood == "angry":
        canvas.create_line(
            x - 12 * scale, y + 26 * scale,
            x + 12 * scale, y + 22 * scale,
            width=3, tags="pet"
        )
    elif mood == "sick":
        canvas.create_arc(
            x - 10 * scale, y + 22 * scale,
            x + 10 * scale, y + 36 * scale,
            start=20, extent=140, style="arc", width=3, tags="pet"
        )
    else:
        canvas.create_arc(
            x - 9 * scale, y + 22 * scale,
            x + 9 * scale, y + 32 * scale,
            start=200, extent=140, style="arc", width=2, tags="pet"
        )


def _face(canvas, x, y, mood, tick, scale=1.0):
    _eyes(canvas, x, y, mood, tick, scale)
    _muzzle(canvas, x, y, scale)
    _mouth(canvas, x, y, mood, scale)
    _whiskers(canvas, x, y, scale)

    if mood == "happy":
        for dx in (-25, 25):
            canvas.create_oval(
                x + dx * scale - 6 * scale, y + 10 * scale,
                x + dx * scale + 6 * scale, y + 20 * scale,
                fill=COLORS["cheek"], outline="", tags="pet"
            )


def _forehead(canvas, x, y, scale=1.0):
    # Hair tuft
    canvas.create_line(
        x, y - 42 * scale,
        x - 5 * scale, y - 58 * scale,
        x + 2 * scale, y - 53 * scale,
        x + 8 * scale, y - 63 * scale,
        smooth=True, width=3, fill=COLORS["outline"], tags="pet"
    )
    # Stripes
    for dx in (-15, 0, 15):
        canvas.create_arc(
            x + dx * scale - 6 * scale, y - 32 * scale,
            x + dx * scale + 6 * scale, y - 8 * scale,
            start=180, extent=180, style="arc", width=2,
            outline=COLORS["stripe"], tags="pet"
        )


def _paws(canvas, x, y, fill, scale=1.0):
    for dx in (-22, 22):
        canvas.create_oval(
            x + dx * scale - 13 * scale, y + 52 * scale,
            x + dx * scale + 13 * scale, y + 77 * scale,
            fill=fill, outline=COLORS["outline"], width=2, tags="pet"
        )
        canvas.create_line(
            x + dx * scale, y + 64 * scale,
            x + dx * scale, y + 74 * scale,
            width=1, tags="pet"
        )


def _draw_cat(canvas, x, y, mood, tick, scale=1.0):
    fill = COLORS[mood]

    _shadow(canvas, x, y, scale)
    _tail(canvas, x, y, tick, mood, scale)
    _body(canvas, x, y, fill, scale)
    _ears(canvas, x, y, fill, scale)
    _head(canvas, x, y, fill, scale)
    _cheeks(canvas, x, y, scale)
    _forehead(canvas, x, y, scale)
    _paws(canvas, x, y, fill, scale)
    _face(canvas, x, y, mood, tick, scale)


# --------------------------------------------------------------------------- #
#  Interactivity helpers
# --------------------------------------------------------------------------- #
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
    if not getattr(canvas, "_cat_click_bound", False):
        canvas.bind("<Button-1>", _on_click)
        canvas._cat_click_bound = True


# --------------------------------------------------------------------------- #
#  Public API (required by pet_animations.py)
# --------------------------------------------------------------------------- #
def draw_idle(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bob = math.sin(tick / 20) * 2
    _draw_cat(canvas, CENTER_X, CENTER_Y + bob, "idle", tick, scale)
    _bind_click_once(canvas)

    # Occasional ear twitch
    if tick % 140 < 6:
        canvas.create_line(
            CENTER_X - 34 * scale, CENTER_Y - 62 * scale,
            CENTER_X - 42 * scale, CENTER_Y - 74 * scale,
            width=2, fill=COLORS["outline"], tags="pet"
        )


def draw_happy(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    bounce = abs(math.sin(tick / 8)) * 6
    _draw_cat(canvas, CENTER_X, CENTER_Y - bounce, "happy", tick, scale)
    _bind_click_once(canvas)

    # Sparkles
    for i in range(3):
        sx = CENTER_X + math.sin(tick / 8 + i * 2) * 50 * scale
        sy = CENTER_Y - 60 * scale + i * 12
        canvas.create_text(
            sx, sy, text="✦", fill="#FFD95A",
            font=("Arial", 10, "bold"), tags="pet"
        )

    if (tick // 20) % 4 == 0:
        canvas.create_text(
            CENTER_X + 50 * scale, CENTER_Y - 55 * scale, text="♥",
            fill="#FF6B8A", font=("Arial", 11, "bold"), tags="pet"
        )


def draw_angry(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    shake = math.sin(tick * 0.8) * 3
    x = CENTER_X + shake
    y = CENTER_Y

    _draw_cat(canvas, x, y, "angry", tick, scale)
    _bind_click_once(canvas)

    # Flattened ears
    canvas.create_line(
        x - 34 * scale, y - 52 * scale,
        x - 48 * scale, y - 42 * scale,
        width=4, fill=COLORS["outline"], tags="pet"
    )
    canvas.create_line(
        x + 34 * scale, y - 52 * scale,
        x + 48 * scale, y - 42 * scale,
        width=4, fill=COLORS["outline"], tags="pet"
    )

    # Puff mark
    canvas.create_text(
        x + 50 * scale, y - 45 * scale, text="💢",
        font=("Arial", 16, "bold"), tags="pet"
    )

    # Motion lines
    for side in (-1, 1):
        canvas.create_line(
            x + side * 55 * scale, y - 8 * scale,
            x + side * 70 * scale, y - 15 * scale,
            width=2, fill=COLORS["outline"], tags="pet"
        )
        canvas.create_line(
            x + side * 55 * scale, y + 10 * scale,
            x + side * 72 * scale, y + 18 * scale,
            width=2, fill=COLORS["outline"], tags="pet"
        )


def draw_sick(canvas, tick, tone_color):
    _clear(canvas)
    scale, _ = _update_interactivity(canvas)
    sway = math.sin(tick / 25) * 4
    x = CENTER_X + sway
    y = CENTER_Y + 3

    _draw_cat(canvas, x, y, "sick", tick, scale)
    _bind_click_once(canvas)

    # Sweat drop
    canvas.create_polygon(
        x + 30 * scale, y - 28 * scale,
        x + 37 * scale, y - 12 * scale,
        x + 24 * scale, y - 12 * scale,
        fill=COLORS["sweat"], outline="", tags="pet"
    )

    # Pale forehead
    canvas.create_arc(
        x - 18 * scale, y - 32 * scale,
        x + 18 * scale, y - 8 * scale,
        start=0, extent=180, fill=COLORS["pale"], outline="", tags="pet"
    )

    # Dizzy stars
    if (tick // 12) % 2 == 0:
        canvas.create_text(
            x - 40 * scale, y - 50 * scale, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )
        canvas.create_text(
            x + 42 * scale, y - 48 * scale, text="✦", fill="#FFE082",
            font=("Arial", 10), tags="pet"
        )

    # Wobble lines
    canvas.create_line(
        x - 28 * scale, y + 55 * scale,
        x - 32 * scale, y + 65 * scale,
        width=2, fill=COLORS["outline"], tags="pet"
    )
    canvas.create_line(
        x + 28 * scale, y + 55 * scale,
        x + 32 * scale, y + 65 * scale,
        width=2, fill=COLORS["outline"], tags="pet"
    )
