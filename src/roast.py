"""
roast.py - Orchestrator.

Ties together GitHub activity fetching, mood detection, roast history,
and the Groq API call, then delivers the result as a Termux notification.
"""

import os
import json
import requests
from datetime import datetime, timezone

from src.config import (
    GITHUB_TOKEN, GROQ_API_KEY, GITHUB_USERNAME,
    GROQ_URL, GROQ_MODEL, STATE_FILE, DATA_DIR, validate_config
)
from src.db import init_db, save_roast, get_recent_roasts
from src.mood import detect_mood

SYSTEM_PROMPT_TEMPLATE = """You are a blunt, sarcastic senior dev roasting a junior dev friend.
Use casual Hinglish, zero corporate fluff, zero motivational fluff.
Keep it short - 2-3 sentences max. Be funny, not mean-spirited.
Current mood context: the user is currently "{mood}".
- happy: they've been active, be a little proud but still teasing
- angry: they've gone quiet for a day, be mildly annoyed
- sick: they've gone quiet for 3+ days, be dramatically disappointed
- idle: nothing notable happened, make idle observations, don't force a roast about work

Do not repeat the themes or jokes from these past roasts:
{history}
"""


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_checked": None, "last_activity": None}


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_github_activity(since_iso):
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    events = resp.json()

    commits, prs = [], []
    latest_ts = None

    for e in events:
        if since_iso and e["created_at"] <= since_iso:
            continue
        latest_ts = e["created_at"] if latest_ts is None else max(latest_ts, e["created_at"])
        if e["type"] == "PushEvent":
            for c in e["payload"].get("commits", []):
                commits.append(c.get("message", ""))
        elif e["type"] == "PullRequestEvent":
            prs.append(e["payload"]["pull_request"].get("title", ""))

    return commits, prs, latest_ts


def build_context(commits, prs):
    lines = []
    lines.append(f"Recent commits: {commits[:5]}" if commits else "No commits since last check.")
    if prs:
        lines.append(f"Recent PRs: {prs[:3]}")
    return "\n".join(lines)


def get_roast(mood, context, history):
    history_text = "\n".join(f"- {h}" for h in history) if history else "(no history yet)"
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(mood=mood, history=history_text)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here's what happened:\n{context}\n\nRoast me."}
        ],
        "max_tokens": 150
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def send_notification(text):
    safe_text = text.replace('"', "'")
    os.system(f'termux-notification --title "Roast Bot" --content "{safe_text}"')


def main():
    validate_config()
    init_db()

    state = load_state()
    commits, prs, latest_ts = get_github_activity(state.get("last_checked"))
    mood = detect_mood(commits, prs, state.get("last_activity"))
    context = build_context(commits, prs)
    history = get_recent_roasts(limit=5)

    roast = get_roast(mood, context, history)
    print(f"[{mood}] {roast}")
    send_notification(roast)
    save_roast(mood, roast)

    state["last_checked"] = datetime.now(timezone.utc).isoformat()
    if latest_ts:
        state["last_activity"] = latest_ts
    save_state(state)


if __name__ == "__main__":
    main()