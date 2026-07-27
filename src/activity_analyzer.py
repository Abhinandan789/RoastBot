"""
activity_analyzer.py - Pattern detection over a batch of ActivityEvents.

Takes SourceSnapshots from one or more data sources and derives
higher-level signals: commit message quality, time-of-day patterns
(converted to local time, not raw UTC), and LeetCode difficulty balance.

Pure analysis - no API calls, no side effects, fully testable in isolation.
"""

from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import List

from src.config import LOCAL_TIMEZONE_OFFSET_HOURS

GOOD_COMMIT_WORDS = {"feat", "feature", "add", "implement", "refactor", "test", "docs", "chore"}
BAD_COMMIT_WORDS = {"fix", "bug", "broken", "hack", "temp", "wip"}
UGLY_COMMIT_WORDS = {"asdf", "testing", "lol", "idk"}


class ActivityAnalyzer:
    def __init__(self, snapshots):
        self.snapshots = {snap.events[0].source if snap.events else f"empty_{i}": snap
                           for i, snap in enumerate(snapshots)}
        self.all_events = []
        for snap in snapshots:
            self.all_events.extend(snap.events)
        self.all_events.sort(key=lambda e: e.timestamp)

    def _to_local(self, dt):
        """Convert a UTC-aware timestamp to local time using the configured offset."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone(timedelta(hours=LOCAL_TIMEZONE_OFFSET_HOURS)))

    def total_activity(self):
        return len(self.all_events)

    def activity_by_source(self):
        return {name: len(snap.events) for name, snap in self.snapshots.items()}

    def is_vampire_coder(self):
        """True if majority of activity happened between local midnight and 6am."""
        if not self.all_events:
            return False
        hours = Counter(self._to_local(e.timestamp).hour for e in self.all_events)
        night = sum(hours.get(h, 0) for h in range(0, 6))
        total = sum(hours.values())
        return total > 0 and (night / total) > 0.5

    def is_weekend_warrior(self):
        if not self.all_events:
            return False
        weekday_count = sum(1 for e in self.all_events if self._to_local(e.timestamp).weekday() < 5)
        weekend_count = sum(1 for e in self.all_events if self._to_local(e.timestamp).weekday() >= 5)
        total = weekday_count + weekend_count
        return total > 0 and (weekend_count / total) > 0.6

    def commit_quality_score(self):
        commits = [e for e in self.all_events if e.category == "commit"]
        if not commits:
            return 50.0

        scores = []
        for c in commits:
            msg = c.title.lower()
            score = 50
            if any(w in msg for w in GOOD_COMMIT_WORDS):
                score += 20
            if len(msg) > 20:
                score += 10
            if any(w in msg for w in BAD_COMMIT_WORDS):
                score -= 15
            if len(msg) < 10:
                score -= 15
            if any(w in msg for w in UGLY_COMMIT_WORDS):
                score -= 30
            scores.append(max(0, min(100, score)))

        return sum(scores) / len(scores)

    def leetcode_difficulty_counts(self):
        lc = self.snapshots.get("leetcode")
        if not lc:
            return {}
        return lc.extras.get("difficulty_counts", {})

    def is_easy_spamming(self):
        """True only if we have real difficulty data AND it's mostly Easy."""
        counts = self.leetcode_difficulty_counts()
        total = sum(v for v in counts.values() if v)
        if total < 3:
            return False
        easy_ratio = counts.get("Easy", 0) / total
        return easy_ratio > 0.8

    def combined_streak(self):
        streaks = [snap.streak_days for snap in self.snapshots.values()]
        return max(streaks) if streaks else 0

    def generate_accountability_report(self):
        lines = []
        by_source = self.activity_by_source()
        lines.append(f"Activity by source: {by_source}" if by_source else "No activity from any source.")

        if self.is_vampire_coder():
            lines.append("Pattern: most activity happened between midnight and 6am local time.")
        if self.is_weekend_warrior():
            lines.append("Pattern: most activity happens on weekends, not weekdays.")

        quality = self.commit_quality_score()
        lines.append(f"Commit quality score: {quality:.0f}/100")

        if self.is_easy_spamming():
            lines.append("Pattern: LeetCode activity is mostly Easy-difficulty problems.")

        streak = self.combined_streak()
        if streak >= 3:
            lines.append(f"Current GitHub activity streak: {streak} days.")

        return "\n".join(lines)