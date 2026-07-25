## v1.0.0
- Added centralized config loader with validation
- Added SQLite-backed roast history (prevents repeated jokes)
- Added mood detection (happy/angry/sick/idle) based on GitHub activity recency
- Refactored monolithic script into src/config.py, src/db.py, src/mood.py, src/roast.py