#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  . "$PROJECT_DIR/.env"
  set +a
fi

export GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export GROQ_API_KEY="${GROQ_API_KEY:-}"
export GITHUB_USERNAME="${GITHUB_USERNAME:-}"

cd "$PROJECT_DIR"
python src/roast.py >> data/roastbot.log 2>&1
