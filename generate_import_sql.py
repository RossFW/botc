#!/usr/bin/env python3
"""
Generate SQL INSERT statements to import gamelog.json into Supabase.

Usage:
    python generate_import_sql.py > import_games.sql
    Then paste the SQL into Supabase SQL Editor and run it.
"""

import json
import os

GAMELOG_FILE = "gamelog.json"
OUTPUT_FILE = "import_games.sql"


def escape_sql_string(s):
    """Escape single quotes for SQL."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def main():
    # Load game log
    if not os.path.exists(GAMELOG_FILE):
        print(f"Error: {GAMELOG_FILE} not found")
        return

    with open(GAMELOG_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)

    print(f"-- Generated SQL to import {len(games)} games from {GAMELOG_FILE}")
    print(f"-- Paste this into Supabase SQL Editor and run it")
    print()

    for game in games:
        game_id = game["game_id"]
        date = escape_sql_string(game.get("date"))
        players_json = json.dumps(game.get("players", []))
        players = escape_sql_string(players_json)
        winning_team = escape_sql_string(game.get("winning_team"))
        game_mode = escape_sql_string(game.get("game_mode"))
        story_teller = escape_sql_string(game.get("story_teller"))

        print(f"INSERT INTO games (game_id, date, players, winning_team, game_mode, story_teller)")
        print(f"VALUES ({game_id}, {date}::timestamptz, {players}::jsonb, {winning_team}, {game_mode}, {story_teller})")
        print(f"ON CONFLICT (game_id) DO NOTHING;")
        print()


if __name__ == "__main__":
    main()
