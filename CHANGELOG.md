## v1.0.0
- Added centralized config loader with validation
- Added SQLite-backed roast history (prevents repeated jokes)
- Added mood detection (happy/angry/sick/idle) based on GitHub activity recency
- Refactored monolithic script into src/config.py, src/db.py, src/mood.py, src/roast.py
## v1.1.0
- Added desktop pet widget (Windows/laptop only): floating always-on-top
  Tkinter window with mood-based animations, auto-popup speech bubble on
  new roasts, and click-to-view roast history panel
- Integrated Respect tone bucket into the roast prompt (warm/neutral/
  cynical/checked_out affects tone)
- Added pet_state.json snapshot mechanism for widget/backend communication