"""
roast.py - Orchestrator.

Ties together GitHub activity fetching, mood detection, respect tracking,
roast history, and the Groq API call, then delivers the result as a
Termux notification and writes a pet-state snapshot for the desktop widget.
"""

import os
import json
import subprocess
import requests
from datetime import datetime, timezone, date

from src.config import (
    GITHUB_TOKEN, GROQ_API_KEY, GITHUB_USERNAME,
    GROQ_URL, GROQ_MODEL, STATE_FILE, PET_STATE_FILE, DATA_DIR, validate_config
)
from src.db import init_db, save_roast, get_recent_roasts
from src.mood import detect_mood
from src.respect import update_respect, get_tone_bucket

SYSTEM_PROMPT_TEMPLATE = """You are a blunt, sarcastic senior dev roasting a junior dev friend.
Use casual casual black English, zero corporate fluff, zero motivational fluff.
Keep it short - 2-3 sentences max. Be funny, not mean-spirited.
Current mood context: the user is currently "{mood}".
- happy: they've been active, be a little proud but still teasing
- angry: they've gone quiet for a day, be mildly annoyed
- sick: they've gone quiet for 3+ days, be dramatically disappointed
- idle: nothing notable happened, make idle observations, don't force a roast about work

Your overall tone toward this user right now is "{tone_bucket}":
- warm: they've been consistent lately, be genuinely encouraging, roast less
- neutral: default sarcastic balance
- cynical: they've disappointed you before, be more pointed and skeptical
- checked_out: you've mostly given up trying to motivate them, be flat and minimal-effort

Do not repeat the themes or jokes from these past roasts:
{history}
"""


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_checked": None,
        "last_activity": None,
        "pet": {"respect": 50, "last_respect_update": None}
    }


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


def get_roast(mood, tone_bucket, context, history):
    history_text = "\n".join(f"- {h}" for h in history) if history else "(no history yet)"
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(mood=mood, tone_bucket=tone_bucket, history=history_text)

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
    try:
        subprocess.run(
            ["termux-notification", "--title", "Roast Bot", "--content", text],
            check=False
        )
    except FileNotFoundError:
        # termux-notification only exists on Termux; safe to skip elsewhere
        print("(notification skipped - not running on Termux)")


def write_pet_snapshot(mood, tone_bucket, respect, roast_text):
    """
    Write a small JSON snapshot for the desktop pet widget to poll.
    This is a read-only data source for pet_widget.py - roast.py is the
    only writer, the widget never writes back to this file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    snapshot = {
        "mood": mood,
        "tone_bucket": tone_bucket,
        "respect": respect,
        "latest_roast": roast_text,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(PET_STATE_FILE, "w") as f:
        json.dump(snapshot, f)


def main():
    validate_config()
    init_db()

    state = load_state()
    pet = state.get("pet", {"respect": 50, "last_respect_update": None})

    commits, prs, latest_ts = get_github_activity(state.get("last_checked"))
    mood = detect_mood(commits, prs, state.get("last_activity"))

    today_str = date.today().isoformat()
    new_respect, new_last_update = update_respect(
        pet.get("respect", 50), mood, pet.get("last_respect_update"), today_str
    )
    tone_bucket = get_tone_bucket(new_respect)

    context = build_context(commits, prs)
    history = get_recent_roasts(limit=5)

    roast = get_roast(mood, tone_bucket, context, history)
    print(f"[{mood}] [respect={new_respect}/{tone_bucket}] {roast}")
    send_notification(roast)
    save_roast(mood, roast)
    write_pet_snapshot(mood, tone_bucket, new_respect, roast)

    state["last_checked"] = datetime.now(timezone.utc).isoformat()
    if latest_ts:
        state["last_activity"] = latest_ts
    state["pet"] = {"respect": new_respect, "last_respect_update": new_last_update}
    save_state(state)


if __name__ == "__main__":
    main()