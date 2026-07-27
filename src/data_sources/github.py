"""
github.py - GitHub activity fetcher, implementing the DataSource interface.

Same fetch logic as the original get_github_activity() in roast.py,
including the merge-based-push fallback fix from v2.1.0 - just reshaped
to return normalized ActivityEvent/SourceSnapshot objects instead of
raw (commits, prs, latest_ts) tuples.
"""

from datetime import datetime, timezone, date, timedelta

import requests

from src.data_sources import DataSource, ActivityEvent, SourceSnapshot
from src.config import GITHUB_TOKEN, GITHUB_USERNAME


class GitHubSource(DataSource):
    @property
    def name(self):
        return "github"

    def health_check(self):
        return bool(GITHUB_TOKEN and GITHUB_USERNAME)

    def fetch(self, since_iso=None) -> SourceSnapshot:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        raw_events = resp.json()

        events = []
        categories = {}
        latest_ts = None
        push_event_count = 0

        for e in raw_events:
            created_at = e["created_at"]
            if since_iso and created_at <= since_iso:
                continue

            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            latest_ts = dt if latest_ts is None else max(latest_ts, dt)

            if e["type"] == "PushEvent":
                push_event_count += 1
                for c in e["payload"].get("commits", []):
                    msg = c.get("message", "")
                    if msg:
                        events.append(ActivityEvent(
                            source="github", timestamp=dt, title=msg,
                            category="commit", metadata={"sha": c.get("sha", "")[:7]}
                        ))
                        categories["commit"] = categories.get("commit", 0) + 1

            elif e["type"] == "PullRequestEvent":
                action = e["payload"].get("action", "")
                title = e["payload"].get("pull_request", {}).get("title", "")
                if title and action in ("opened", "closed"):
                    events.append(ActivityEvent(
                        source="github", timestamp=dt, title=title,
                        category="pr", metadata={"action": action}
                    ))
                    categories["pr"] = categories.get("pr", 0) + 1

        # Fallback: merge-based pushes can have empty commit payloads
        # (GitHub's distinct_size: 0 case) - still count as real activity.
        if not events and push_event_count > 0:
            events.append(ActivityEvent(
                source="github", timestamp=latest_ts or datetime.now(timezone.utc),
                title=f"{push_event_count} push event(s) detected (merge/PR-based activity)",
                category="commit", metadata={"fallback": True}
            ))
            categories["commit"] = push_event_count

        streak = self._calc_streak(raw_events)

        return SourceSnapshot(
            events=events,
            streak_days=streak,
            total_count=len(events),
            last_activity=latest_ts,
            categories=categories,
            extras={"raw_event_count": len(raw_events)}
        )

    def _calc_streak(self, raw_events):
        dates = set()
        for e in raw_events:
            d = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).date()
            dates.add(d)

        streak = 0
        today = date.today()
        for i in range(30):
            if today - timedelta(days=i) in dates:
                streak += 1
            else:
                break
        return streak