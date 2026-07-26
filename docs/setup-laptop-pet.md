# Desktop Pet Widget Setup (Laptop, Windows only)

This feature adds a small always-on-top floating pet to your desktop.
It reacts to your GitHub activity mood (happy/angry/sick/idle) and shows
an auto-popping speech bubble with your latest roast whenever roast.py
runs. Click the pet to see your last 10 roasts.

This is laptop-only. It does not run on the phone/Termux side - Tkinter
does not work well on Android without significant extra setup, so the
phone continues using notification-only delivery.

## Prerequisites
- Windows
- Python 3.x with Tkinter (included in standard python.org installs)
- The existing RoastBot venv and .env already set up (see main README)

## Setup steps

1. Confirm Tkinter is available: python -c "import tkinter; print('ok')"
If this fails, reinstall Python from python.org and ensure the
   "tcl/tk and IDLE" option is checked during install.

2. Test launching the widget manually: python -m src.pet_widget
You should see a small floating window with an animated pet.

3. In a separate terminal, run the roast pipeline once to confirm the
   two processes talk to each other: python -m src.roast
   Within ~4 seconds, a speech bubble should appear on the pet with the
   generated roast text.

4. Click the pet - a history panel should open showing recent roasts.

5. Right-click the pet to close it.

## Enabling autostart (optional but recommended)

1. Press `Win+R`, type `shell:startup`, press Enter.
2. Right-click `scripts\start_pet.bat` in File Explorer, choose
   "Create shortcut".
3. Move that shortcut into the Startup folder that opened in step 1.
4. Restart your laptop (or log out/in) to confirm it launches
   automatically.

## How it works (architecture summary)

roast.py writes a small JSON snapshot (data/pet_state.json) after every
run. pet_widget.py is a completely separate, independent process that
polls that file every 4 seconds - there is no server, no HTTP, no shared
Python state between the two processes. If one crashes, the other keeps
working. This was a deliberate simplification over an earlier considered
approach (a local HTTP server + browser page), chosen because it removes
an entire class of failure modes (server crashes, port conflicts) for a
laptop-only, single-user tool.

## Known limitations

- The widget does not persist its screen position across restarts -
  it always reopens in the same default location.
- MIUI-style aggressive background killing is not a laptop concern, but
  if Windows ever suspends the process (e.g. during sleep), it should
  resume normally on wake - not extensively tested across sleep/wake
  cycles yet.
- No sound/TTS - deferred, matches the original project roadmap.
        