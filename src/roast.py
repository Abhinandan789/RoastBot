"""
roast.py - Orchestrator.

Ties together multi-source activity fetching (GitHub, LeetCode),
pattern analysis, goal tracking, mood detection, respect tracking, and
the Groq API call, then delivers the result as a Termux notification
and writes a pet-state snapshot for the desktop widget.
"""

import os
import json
import subprocess
import requests
from datetime import datetime, timezone, date

from src.config import (
    GROQ_API_KEY, GROQ_URL, GROQ_MODEL,
    STATE_FILE, PET_STATE_FILE, DATA_DIR, validate_config
)
from src.db import init_db, save_roast, get_recent_roasts
from src.mood import detect_mood
from src.respect import update_respect, get_tone_bucket
from src.data_sources.github import GitHubSource
from src.data_sources.leetcode import LeetCodeSource
from src.activity_analyzer import ActivityAnalyzer
from src.goals import record_events, build_goal_status_text

SYSTEM_PROMPT_TEMPLATE = """You are a blunt, sarcastic senior dev roasting a junior dev friend.
Use casual Black English, zero corporate fluff, zero motivational fluff.
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

Accountability data (use specifics from here if relevant, don't force all of it in):
{accountability_report}

Goal status:
{goal_status}

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


def fetch_all_sources(since_iso):
    """Returns (snapshots, latest_activity_iso)."""
    snapshots = []
    latest = None

    gh = GitHubSource()
    if gh.health_check():
        snap = gh.fetch(since_iso)
        snapshots.append(snap)
        if snap.last_activity:
            latest = snap.last_activity if latest is None else max(latest, snap.last_activity)

    lc = LeetCodeSource()
    if lc.health_check():
        snap = lc.fetch(since_iso)
        snapshots.append(snap)
        if snap.last_activity:
            latest = snap.last_activity if latest is None else max(latest, snap.last_activity)

    latest_iso = latest.isoformat() if latest else None
    return snapshots, latest_iso


def get_roast(mood, tone_bucket, accountability_report, goal_status, history):
    history_text = "\n".join(f"- {h}" for h in history) if history else "(no history yet)"
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        mood=mood, tone_bucket=tone_bucket,
        accountability_report=accountability_report,
        goal_status=goal_status, history=history_text
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Roast me based on what happened."}
        ],
        "max_tokens": 180
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
        print("(notification skipped - not running on Termux)")


def write_pet_snapshot(mood, tone_bucket, respect, roast_text):
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

    snapshots, latest_activity_iso = fetch_all_sources(state.get("last_checked"))

    all_events = []
    for snap in snapshots:
        all_events.extend(snap.events)
        record_events(snap.events, snap.events[0].source if snap.events else "unknown")

    analyzer = ActivityAnalyzer(snapshots)
    accountability_report = analyzer.generate_accountability_report()
    goal_status = build_goal_status_text()

    mood = detect_mood(len(all_events), state.get("last_activity"))

    today_str = date.today().isoformat()
    new_respect, new_last_update = update_respect(
        pet.get("respect", 50), mood, pet.get("last_respect_update"), today_str
    )
    tone_bucket = get_tone_bucket(new_respect)

    history = get_recent_roasts(limit=5)
    roast = get_roast(mood, tone_bucket, accountability_report, goal_status, history)

    print(f"[{mood}] [respect={new_respect}/{tone_bucket}] {roast}")
    send_notification(roast)
    save_roast(mood, roast)
    write_pet_snapshot(mood, tone_bucket, new_respect, roast)

    state["last_checked"] = datetime.now(timezone.utc).isoformat()
    if latest_activity_iso:
        state["last_activity"] = latest_activity_iso
    state["pet"] = {"respect": new_respect, "last_respect_update": new_last_update}
    save_state(state)


if __name__ == "__main__":
    main()