"""
mood.py - Mood detection logic.

Single responsibility: take raw GitHub activity (commits, PRs, and the
timestamp of the last known activity) and return a single mood label.
No API calls happen here - pure decision logic only.
"""

from datetime import datetime, timezone

VALID_MOODS = ("happy", "angry", "sick", "idle")


def detect_mood(commits, prs, last_activity_iso):
    """
    Decide the current mood based on activity signals.

    commits: list of commit message strings since last check
    prs: list of PR title strings since last check
    last_activity_iso: ISO timestamp string of the last known GitHub activity,
                        or None if never checked before / no activity found
    """
    if commits or prs:
        return "happy"

    if last_activity_iso is None:
        return "idle"

    last_activity = datetime.fromisoformat(last_activity_iso)
    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)

    days_since = (datetime.now(timezone.utc) - last_activity).days

    if days_since >= 3:
        return "sick"
    if days_since >= 1:
        return "angry"

    return "idle"