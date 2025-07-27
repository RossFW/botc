"""
Script to modernize Blood on the Clocktower Elo JSON data.

This script updates the existing `gamelog.json` and `players.json` files to
include additional metadata introduced in the updated Elo tracker:

* Adds a `story_teller` field to every game (set to "Matan_Diamond" by default).
* Adds a `game_mode` field to every game (empty string to be filled manually).
* For each player in every game:
  - Creates a `roles` list containing every role they played during the game.
    The existing `role` field is interpreted as the final role; if the string
    contains `+` characters (e.g. "Virgin+Witch"), it is split and all roles
    are normalised and stored.
  - Normalises the `role` field to consistent capitalisation and underscore
    formatting.
  - Adds an `initial_team` field equal to their final team (since legacy
    data does not record alignment changes).

After updating the game log, the script recalculates all player ratings
and writes out a fresh `players.json` using the modernised game data and
the updated `botc_elo.py` module.

Usage:
    python3 convert_to_modern_format.py

Make sure this script and `botc_elo.py` live alongside the existing
`gamelog.json` and `players.json` files in your repository. Running this script
will overwrite those JSON files in place.
"""

import json
import os
from typing import List

import botc_elo


def standardize_role(role_part: str) -> str:
    """Use the same normalisation logic as the GUI for role names."""
    return botc_elo.EloTrackerApp._standardize_role(role_part)


def modernize_gamelog(filename: str) -> List[dict]:
    """Load and update the gamelog in-place, returning the updated list."""
    with open(filename, "r", encoding="utf-8") as f:
        games = json.load(f)
    for game in games:
        # Ensure new metadata exists
        game["game_mode"] = game.get("game_mode", "")
        # Set a default story teller if missing
        game["story_teller"] = "Matan_Diamond"
        for p in game.get("players", []):
            # Normalise and split role string into history
            role_str = p.get("role", "")
            raw_roles = []
            if role_str:
                raw_roles = role_str.split("+")
            # Standardise each role and derive final role
            roles = [standardize_role(r) for r in raw_roles] if raw_roles else []
            final_role = roles[-1] if roles else ""
            p["roles"] = roles
            p["role"] = final_role
            # Record the starting alignment; legacy data assumes no alignment change
            p["initial_team"] = p.get("team")
    # Write the updated log back to disk
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2)
    return games


def rebuild_players(games: List[dict]) -> None:
    """Recalculate player ratings and histories from a list of games."""
    # Clear existing globals in the botc_elo module
    botc_elo.players.clear()
    botc_elo.game_log.clear()
    botc_elo.game_log.extend(games)
    botc_elo.recalc_all()
    botc_elo.save_data()


def main() -> None:
    # Determine the paths to gamelog and players files
    log_path = botc_elo.GAMELOG_FILE
    players_path = botc_elo.PLAYERS_FILE
    if not os.path.isfile(log_path):
        raise FileNotFoundError(f"Expected {log_path} to exist in the current directory.")
    if not os.path.isfile(players_path):
        raise FileNotFoundError(f"Expected {players_path} to exist in the current directory.")
    # Update the gamelog and write changes
    games = modernize_gamelog(log_path)
    # Rebuild players.json from the updated game log
    rebuild_players(games)
    print("Modernisation complete. Updated gamelog.json and players.json have been saved.")


if __name__ == "__main__":
    main()