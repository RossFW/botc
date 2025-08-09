# Blood on the Clocktower Elo

A simple desktop app to track player Elo ratings and win percentages for Blood on the Clocktower (BOTC) games, plus a separate analytics dashboard focused on games run by a specific storyteller.

## Contents
- `botc_elo.py`: Tkinter app to enter games, compute Elo, and visualize per‑player history
- `analytics_matan.py`: Tkinter dashboard surfacing script/character/player stats for a storyteller (default: `Matan_Diamond`)
- `gamelog.json`: Append‑only list of games submitted in the app
- `players.json`: Snapshot of computed player states and histories
- `naming convention.txt`: Short notes on text entry format

## Requirements
- Python 3.9+ (3.11 recommended)
- Tkinter (bundled with python.org installers; on macOS ensure a recent Tcl/Tk)
- Packages:
  - `matplotlib`
  - `numpy` (used for plotting convenience)

Install packages:

```bash
python3 -m pip install matplotlib numpy
```

## Quick Start
1. Open a terminal in this folder.
2. Launch the Elo tracker UI:

   ```bash
   python3 botc_elo.py
   ```

3. Optionally, open the analytics dashboard (read‑only, uses `gamelog.json`):

   ```bash
   python3 analytics_matan.py
   ```

Both apps read/write `players.json` and `gamelog.json` in the current directory.

## Using the Elo Tracker (botc_elo.py)
### Entering a game
- Fill the two text boxes: one line per player per team.
- Choose which team is Evil and who won via the radio buttons.
- Select or type a script name in Game Mode (dropdown is editable).
- Optionally enter the storyteller name.
- Click “Submit Game”. Ratings and win rates update immediately.

### Line format in team boxes
Each line:

```
Name Role [InitialTeam]
```

- Name: use underscores instead of spaces (e.g., `Ross_Williams`).
- Role: case‑insensitive; multi‑word roles use underscores (e.g., `Snake_Charmer`). If a player changed roles, join with `+` (e.g., `Virgin+Witch`). The final role is the last one.
- InitialTeam (optional): starting alignment, or start->end if it changed (e.g., `Good`, `Evil`, or `Good->Evil`). If omitted, the app assumes the player started on the same team they finished on.

Examples:

```
Ross_Williams Chambermaid
Zoe_Diamond Snake_Charmer Good->Evil
Eitan_Ghelman Virgin+Witch Good
```

Tips:
- Put each player in the box for the team they finished on; use `Good->Evil` or `Evil->Good` to record starting team when relevant.
- Role capitalization and underscores are standardized automatically.

### Editing or deleting games
- Click “Edit Game Log” to open the list of submitted games.
- Select a game to edit lines/assignments or to delete it.
- Saving or deleting will automatically recalculate Elo and write updated JSON files.

### Viewing player charts
- Double‑click a player row in the main table to open a chart of rating and win‑percentage history over game number.

## Data Files
- `gamelog.json`: list of games with fields: `game_id`, `date`, `players` (with `name`, `role`, `roles`, `team`, `initial_team`), `winning_team`, `game_mode`, `story_teller`.
- `players.json`: list of players with `current_rating`, `rating_history`, and `game_history` derived from the game log.

You can back up or version these JSON files; the app will rebuild player stats from `gamelog.json` if needed.

## Analytics Dashboard (analytics_matan.py)
Run:

```bash
python3 analytics_matan.py
```

Features:
- Scripts tab: Good/Evil win rates and totals per script, plus category totals
- Characters tab: role appearance and win rates across selected scripts/categories
- Players tab: per‑player overall and per‑script win rates; double‑click for role/script details

Configuration:
- Target storyteller is set by `TARGET_STORYTELLER` at the top of `analytics_matan.py` (default: `Matan_Diamond`).
- Scripts categorized as “Normal” vs “Teensyville” by the `NORMAL_SCRIPTS` set.

## Troubleshooting
- Tkinter on macOS: If the UI fails to launch, install Python from python.org (which bundles Tk) or ensure a recent Tcl/Tk is installed.
- Matplotlib backend: If plots don’t show, upgrade matplotlib or run from a desktop session (not a headless shell).

## License
Personal project; no specific license declared. Ask the author before redistribution.

