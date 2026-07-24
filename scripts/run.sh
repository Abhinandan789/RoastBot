#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  . "$PROJECT_DIR/.env"
  set +a
fi

: "${GITHUB_TOKEN:?GITHUB_TOKEN must be set (see .env.example)}"
: "${GROQ_API_KEY:?GROQ_API_KEY must be set (see .env.example)}"
: "${GITHUB_USERNAME:?GITHUB_USERNAME must be set (see .env.example)}"

cd "$PROJECT_DIR"
mkdir -p data
python src/roast.py >> data/roastbot.log 2>&1
