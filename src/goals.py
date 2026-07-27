"""
goals.py - Optional accountability goals with progress tracking.

Goals are stored in data/goals.json (user-editable, has sane defaults).
Progress is tracked per period (daily/weekly) in data/goal_progress.json.

record_activity() is idempotent per event: callers must pass a stable
event_id so the same real-world event is never counted twice, even if
roast.py's "since last check" window has any overlap bug.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import date
from typing import List, Optional

from src.config import DATA_DIR

GOALS_FILE = os.path.join(DATA_DIR, "goals.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "goal_progress.json")


@dataclass
class Goal:
    id: str
    name: str
    source: str          # "github", "leetcode", "any"
    category: str         # "commit", "pr", "submission"
    target_count: int
    period: str            # "daily" or "weekly"
    active: bool = True


DEFAULT_GOALS = [
    Goal("daily_commits", "Daily Commits", "github", "commit", 1, "daily"),
    Goal("daily_leetcode", "Daily LeetCode", "leetcode", "submission", 1, "daily"),
]


def load_goals() -> List[Goal]:
    if not os.path.exists(GOALS_FILE):
        save_goals(DEFAULT_GOALS)
        return DEFAULT_GOALS
    with open(GOALS_FILE) as f:
        data = json.load(f)
        return [Goal(**g) for g in data]


def save_goals(goals: List[Goal]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(GOALS_FILE, "w") as f:
        json.dump([asdict(g) for g in goals], f, indent=2)


def _load_progress() -> dict:
    if not os.path.exists(PROGRESS_FILE):
        return {"counts": {}, "seen_event_ids": []}
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def _save_progress(progress: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def _period_key(period: str) -> str:
    today = date.today()
    if period == "weekly":
        return f"{today.year}-W{today.isocalendar()[1]:02d}"
    return today.isoformat()


def record_events(events, source_name):
    """
    events: list of ActivityEvent objects (from data_sources).
    Each event's (source, category, timestamp) forms a stable id so the
    same real event is never double-counted across runs, even if the
    same event somehow appears in two consecutive fetch windows.
    """
    goals = load_goals()
    progress = _load_progress()
    seen = set(progress.get("seen_event_ids", []))
    counts = progress.get("counts", {})

    for event in events:
        event_id = f"{event.source}:{event.category}:{event.timestamp.isoformat()}"
        if event_id in seen:
            continue
        seen.add(event_id)

        for goal in goals:
            if not goal.active:
                continue
            if goal.source not in (event.source, "any"):
                continue
            if goal.category != event.category:
                continue
            key = f"{goal.id}:{_period_key(goal.period)}"
            counts[key] = counts.get(key, 0) + 1

    progress["seen_event_ids"] = list(seen)[-2000:]  # cap growth, keep recent history
    progress["counts"] = counts
    _save_progress(progress)


def check_goals() -> List[dict]:
    goals = load_goals()
    progress = _load_progress()
    counts = progress.get("counts", {})
    results = []

    for goal in goals:
        if not goal.active:
            continue
        key = f"{goal.id}:{_period_key(goal.period)}"
        current = counts.get(key, 0)
        pct = (current / goal.target_count * 100) if goal.target_count else 0
        status = "met" if pct >= 100 else ("in_progress" if pct > 0 else "not_started")
        results.append({
            "goal": goal, "current": current, "target": goal.target_count,
            "percentage": round(pct, 1), "status": status
        })

    return results


def build_goal_status_text() -> str:
    results = check_goals()
    if not results:
        return "No goals configured."
    lines = []
    for r in results:
        marker = {"met": "[MET]", "in_progress": "[IN PROGRESS]", "not_started": "[NOT STARTED]"}[r["status"]]
        lines.append(f"{marker} {r['goal'].name}: {r['current']}/{r['target']}")
    return "\n".join(lines)