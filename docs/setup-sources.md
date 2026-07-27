# Configuring Additional Activity Sources (v3.0.0+)

RoastBot can now track activity beyond GitHub. Each source is optional -
if unconfigured, it's silently skipped, no crash.

## LeetCode

Add to `.env`: LEETCODE_USERNAME=your_leetcode_username

Requires your LeetCode submissions to be set to public in your LeetCode
profile privacy settings, or recent submissions won't be visible via
the public API.

## Local timezone (for pattern detection)

Add to `.env`: LOCAL_TIMEZONE_OFFSET_HOURS=5

Used by activity_analyzer.py to correctly classify "vampire coding"
(late night activity) and weekend patterns in your actual local time,
not raw UTC.

## Goals

Goals are auto-created with sensible defaults on first run, stored in
`data/goals.json` (gitignored, local only). Edit that file directly to
change targets - no code changes needed. Example:
```json
[
  {"id": "daily_commits", "name": "Daily Commits", "source": "github",
   "category": "commit", "target_count": 1, "period": "daily", "active": true}
]
```