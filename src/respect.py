"""
respect.py - Tracks and interprets the hidden Respect stat.

Single responsibility: given the current respect value, today's mood,
and when respect was last updated, decide the new respect value and
which tone bucket it falls into. This is a separate concern from
mood.py (which only converts activity into a mood label) - Respect is
a parallel axis, not the same computation.

Update rule: respect only changes once per calendar day, on the first
run of the day that resolves to a "happy" (gain) or "angry"/"sick"
(loss) mood. Multiple runs on the same day, or an "idle" mood, do not
move the number - this prevents gaming the stat with rapid repeated
activity in a single day.
"""

RESPECT_START = 50
RESPECT_GAIN = 3
RESPECT_LOSS = -6


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def update_respect(current_respect, mood, last_update_date, today):
    """
    Returns a tuple: (new_respect, new_last_update_date)

    current_respect: int, the respect value before this run
    mood: str, one of "happy", "angry", "sick", "idle"
    last_update_date: str (ISO date, e.g. "2026-07-25") or None
    today: str (ISO date for the current run)
    """
    if last_update_date == today:
        return current_respect, last_update_date  # already updated today, no-op

    if mood == "happy":
        return clamp(current_respect + RESPECT_GAIN), today
    if mood in ("angry", "sick"):
        return clamp(current_respect + RESPECT_LOSS), today

    return current_respect, last_update_date  # idle: no change, no date update


def get_tone_bucket(respect):
    """
    Maps a respect value (0-100) to one of four tone buckets, used to
    shift the roast prompt's tone.
    """
    if respect >= 80:
        return "warm"
    if respect >= 50:
        return "neutral"
    if respect >= 20:
        return "cynical"
    return "checked_out"