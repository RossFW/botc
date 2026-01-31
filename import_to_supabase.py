#!/usr/bin/env python3
"""
Import existing gamelog.json data into Supabase.

Usage:
    pip install supabase
    python import_to_supabase.py
"""

import json
import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://mfwigdvxwpdemmwwskyk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1md2lnZHZ4d3BkZW1td3dza3lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NzY3NzMsImV4cCI6MjA4NTQ1Mjc3M30.KKAP1Tovgykk6iM6QHy_0-JHCik2Tp_6ja1T00shIDs"

# File path
GAMELOG_FILE = "gamelog.json"


def main():
    # Load game log
    if not os.path.exists(GAMELOG_FILE):
        print(f"Error: {GAMELOG_FILE} not found")
        return

    with open(GAMELOG_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)

    print(f"Loaded {len(games)} games from {GAMELOG_FILE}")

    # Connect to Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected to Supabase")

    # Check if games table already has data
    existing = supabase.table("games").select("game_id").execute()
    if existing.data:
        print(f"Warning: games table already has {len(existing.data)} records")
        response = input("Do you want to continue and add more? (y/n): ")
        if response.lower() != "y":
            print("Aborted")
            return
        existing_ids = {g["game_id"] for g in existing.data}
    else:
        existing_ids = set()

    # Import games
    imported = 0
    skipped = 0
    errors = 0

    for game in games:
        game_id = game["game_id"]

        # Skip if already exists
        if game_id in existing_ids:
            skipped += 1
            continue

        try:
            # Prepare record for Supabase
            record = {
                "game_id": game_id,
                "date": game.get("date"),
                "players": game.get("players", []),
                "winning_team": game.get("winning_team"),
                "game_mode": game.get("game_mode"),
                "story_teller": game.get("story_teller"),
            }

            # Insert into Supabase
            result = supabase.table("games").insert(record).execute()

            if result.data:
                imported += 1
                if imported % 10 == 0:
                    print(f"  Imported {imported} games...")
            else:
                errors += 1
                print(f"  Error importing game {game_id}")

        except Exception as e:
            errors += 1
            print(f"  Error importing game {game_id}: {e}")

    print(f"\nDone!")
    print(f"  Imported: {imported}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Errors: {errors}")


if __name__ == "__main__":
    main()
