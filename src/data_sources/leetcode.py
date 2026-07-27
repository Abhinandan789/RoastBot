"""
leetcode.py - LeetCode activity fetcher via their public GraphQL API.

No auth token needed - only your username, since this reads public
submission data. Difficulty per submission is fetched via a second,
per-problem query (LeetCode's recent-submissions endpoint doesn't
include difficulty directly) - results are cached in-memory per run
to avoid redundant calls for the same problem.
"""

from datetime import datetime, timezone

import requests

from src.data_sources import DataSource, ActivityEvent, SourceSnapshot
from src.config import LEETCODE_USERNAME

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {"Content-Type": "application/json", "Referer": "https://leetcode.com/"}

RECENT_SUBMISSIONS_QUERY = """
query recentSubmissions($username: String!) {
  recentSubmissionList(username: $username, limit: 20) {
    title
    titleSlug
    timestamp
    statusDisplay
  }
}
"""

PROBLEM_DIFFICULTY_QUERY = """
query problemDifficulty($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    difficulty
  }
}
"""

PROFILE_QUERY = """
query userProfile($username: String!) {
  matchedUser(username: $username) {
    submitStats {
      acSubmissionNum { difficulty count }
    }
  }
}
"""


class LeetCodeSource(DataSource):
    def __init__(self):
        self._difficulty_cache = {}

    @property
    def name(self):
        return "leetcode"

    def health_check(self):
        return bool(LEETCODE_USERNAME)

    def fetch(self, since_iso=None) -> SourceSnapshot:
        submissions = self._fetch_recent_submissions()
        events = []
        difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        latest_ts = None

        since_dt = None
        if since_iso:
            since_dt = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))

        for sub in submissions:
            ts = sub.get("timestamp")
            if not ts:
                continue
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
            if since_dt and dt <= since_dt:
                continue
            if sub.get("statusDisplay") != "Accepted":
                continue

            latest_ts = dt if latest_ts is None else max(latest_ts, dt)
            title_slug = sub.get("titleSlug", "")
            difficulty = self._get_difficulty(title_slug)
            if difficulty:
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

            events.append(ActivityEvent(
                source="leetcode", timestamp=dt, title=sub.get("title", ""),
                category="submission", metadata={"difficulty": difficulty}
            ))

        total_solved = self._fetch_total_solved()

        return SourceSnapshot(
            events=events,
            streak_days=0,  # LeetCode's public API doesn't expose streak reliably
            total_count=len(events),
            last_activity=latest_ts,
            categories={"submission": len(events)},
            extras={"difficulty_counts": difficulty_counts, "total_solved": total_solved}
        )

    def _fetch_recent_submissions(self):
        try:
            resp = requests.post(
                GRAPHQL_URL,
                json={"query": RECENT_SUBMISSIONS_QUERY, "variables": {"username": LEETCODE_USERNAME}},
                headers=HEADERS, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("recentSubmissionList") or []
        except (requests.RequestException, ValueError):
            return []

    def _get_difficulty(self, title_slug):
        if not title_slug:
            return None
        if title_slug in self._difficulty_cache:
            return self._difficulty_cache[title_slug]
        try:
            resp = requests.post(
                GRAPHQL_URL,
                json={"query": PROBLEM_DIFFICULTY_QUERY, "variables": {"titleSlug": title_slug}},
                headers=HEADERS, timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            difficulty = data.get("data", {}).get("question", {}).get("difficulty")
            self._difficulty_cache[title_slug] = difficulty
            return difficulty
        except (requests.RequestException, ValueError):
            return None

    def _fetch_total_solved(self):
        try:
            resp = requests.post(
                GRAPHQL_URL,
                json={"query": PROFILE_QUERY, "variables": {"username": LEETCODE_USERNAME}},
                headers=HEADERS, timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            user = data.get("data", {}).get("matchedUser")
            if not user:
                return 0
            for item in user.get("submitStats", {}).get("acSubmissionNum", []):
                if item["difficulty"] == "All":
                    return item["count"]
            return 0
        except (requests.RequestException, ValueError):
            return 0