## v1.0.0
- Added centralized config loader with validation
- Added SQLite-backed roast history (prevents repeated jokes)
- Added mood detection (happy/angry/sick/idle) based on GitHub activity recency
- Refactored monolithic script into src/config.py, src/db.py, src/mood.py, src/roast.py
## v2.0.0
- Desktop pet widget: floating always-on-top window with mood animations,
  auto-popup speech bubble (in its own independent Toplevel), and
  click-to-view roast history panel
- Note: history panel (originally scoped as a separate Stage 4) was
  implemented together with Stage 3's bubble rework, since both touched
  pet_widget.py in the same session - no separate PR exists for it,
  intentionally, to avoid a no-op PR

## v2.2.0
- Added multi-source activity tracking: GitHub (existing) + LeetCode (new)
- Added ActivityAnalyzer: commit quality scoring, vampire-coder and
  weekend-warrior pattern detection (timezone-correct), LeetCode
  difficulty balance
- Added optional goal tracking (daily/weekly targets) with idempotent
  event-based progress counting
- roast.py and mood.py extended in place to use the new multi-source
  pipeline - no parallel/forked files introduced
  Added five new pet designs: droplet, cat, ghost, robot, smiley2 -
  alongside the original smiley - all selectable via ACTIVE_PET in .env
- Changed default pet from smiley to droplet
- Added tools/pet_face_tester.py: a standalone visual tester that
  auto-discovers all registered pets and renders every mood
  (idle/happy/angry/sick) side by side for design comparison before
  committing to a look