# Architecture

RoastBot first fetches recent activity from the GitHub API. That activity is passed to `mood.py`, which determines the current mood state. Next, `db.py` checks roast history so the bot avoids repeating similar roasts. Then `roast.py` builds the final prompt and calls the Groq API to generate a roast. Finally, the generated result is sent to Android using `termux-notification`.
