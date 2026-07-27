"""
mood.py - Mood detection logic.

Single responsibility: given aggregated activity signals from one or
more sources, plus goal status, return a single mood label. Pure
decision logic - no API calls, no side effects.
"""

from datetime import datetime, timezone

VALID_MOODS = ("happy", "angry", "sick", "idle")


def detect_mood(total_activity_count, last_activity_iso, missed_goal_with_no_activity=False):
    """
    total_activity_count: int, count of ActivityEvents across all sources
                           since last check
    last_activity_iso: ISO timestamp of last known activity across all
                        sources, or None
    missed_goal_with_no_activity: True if a goal period ended (e.g. end
                                   of week) with zero matching activity
    """
    if total_activity_count > 0:
        return "happy"

    if missed_goal_with_no_activity:
        return "sick"

    if last_activity_iso is None:
        return "idle"

    last_activity = datetime.fromisoformat(last_activity_iso.replace("Z", "+00:00"))
    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)

    days_since = (datetime.now(timezone.utc) - last_activity).days

    if days_since >= 3:
        return "sick"
    if days_since >= 1:
        return "angry"

    return "idle"