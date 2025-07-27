import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime

# ---------------------------
# Global Constants / Defaults
# ---------------------------
DEFAULT_RATING = 1500
ELO_K_FACTOR = 32
RATINGS_FILE = "botc_final_ratings.xlsx"
GAME_LOG_FILE = "botc_game_log.xlsx"

# ---------------------------
# Global In-Memory Data
# ---------------------------
player_ratings = {}   # Dictionary: { player_name: rating }
player_game_log = []  # List of dicts: each record is one row for one player in one game.

# ---------------------------
# Utility Functions
# ---------------------------
def load_existing_data():
    """
    Loads existing player ratings and game log from Excel files, if they exist.
    Populates player_ratings and returns a DataFrame for the existing game log.
    """
    # Load ratings
    if os.path.isfile(RATINGS_FILE):
        df_ratings = pd.read_excel(RATINGS_FILE)
        # Convert to dict
        for _, row in df_ratings.iterrows():
            player_ratings[row["player"]] = row["rating"]
    else:
        # No ratings file yet
        pass

    # Load game log
    if os.path.isfile(GAME_LOG_FILE):
        df_log = pd.read_excel(GAME_LOG_FILE)
    else:
        df_log = pd.DataFrame(columns=["game_id", "date", "player_name", "team",
                                       "role", "did_win"])

    return df_log

def save_ratings_to_excel():
    """
    Saves the current player_ratings dict to RATINGS_FILE as an Excel sheet.
    """
    data = [{"player": p, "rating": r} for p, r in player_ratings.items()]
    df_elo = pd.DataFrame(data)
    df_elo.to_excel(RATINGS_FILE, index=False)

def save_game_log_to_excel(df_log):
    """
    Saves the provided DataFrame df_log to GAME_LOG_FILE as an Excel sheet.
    """
    df_log.to_excel(GAME_LOG_FILE, index=False)

def expected_score(ratingA, ratingB):
    """
    Standard Elo expected score formula.
    """
    return 1.0 / (1.0 + 10 ** ((ratingB - ratingA) / 400))

def calculate_team_average(team_players):
    """
    Given a list of dictionaries (with "name" key),
    return the average rating from player_ratings (or DEFAULT_RATING if new).
    """
    if not team_players:
        return DEFAULT_RATING
    total = 0
    for p in team_players:
        r = player_ratings.get(p["name"], DEFAULT_RATING)
        total += r
    return total / len(team_players)

def update_elo_for_game(game):
    """
    Updates the global player_ratings based on the game result.
    game is a dict with:
      "players" : list of { "name", "team" }
      "winning_team": "Good" or "Evil"
    """
    # Separate players
    good_team = [p for p in game["players"] if p["team"] == "Good"]
    evil_team = [p for p in game["players"] if p["team"] == "Evil"]

    # Calculate average ratings
    good_team_rating = calculate_team_average(good_team)
    evil_team_rating = calculate_team_average(evil_team)

    # Compute expected scores
    E_good = expected_score(good_team_rating, evil_team_rating)
    E_evil = 1.0 - E_good

    # Actual results
    if game["winning_team"] == "Good":
        S_good, S_evil = 1, 0
    else:
        S_good, S_evil = 0, 1

    # Update Good team
    for p in good_team:
        old_rating = player_ratings.get(p["name"], DEFAULT_RATING)
        new_rating = old_rating + ELO_K_FACTOR * (S_good - E_good)
        player_ratings[p["name"]] = new_rating

    # Update Evil team
    for p in evil_team:
        old_rating = player_ratings.get(p["name"], DEFAULT_RATING)
        new_rating = old_rating + ELO_K_FACTOR * (S_evil - E_evil)
        player_ratings[p["name"]] = new_rating


# ---------------------------
# Main UI / Tkinter
# ---------------------------
class BotCEloApp:
    def __init__(self, master):
        self.master = master
        master.title("Blood on the Clocktower Elo Tracker")

        # We'll load existing log DataFrame
        self.df_log = load_existing_data()

        # For assigning a new game_id, we look at max existing, or default to 0.
        if not self.df_log.empty:
            self.next_game_id = self.df_log["game_id"].max() + 1
        else:
            self.next_game_id = 1

        # ---------- LAYOUT ----------
        # Team 1 frame
        frame_team1 = tk.LabelFrame(master, text="Team 1 (One player per line: Name Role)")
        frame_team1.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.text_team1 = tk.Text(frame_team1, width=40, height=10)
        self.text_team1.pack(padx=5, pady=5)

        # Team 2 frame
        frame_team2 = tk.LabelFrame(master, text="Team 2 (One player per line: Name Role)")
        frame_team2.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.text_team2 = tk.Text(frame_team2, width=40, height=10)
        self.text_team2.pack(padx=5, pady=5)

        # Evil/Good selection
        frame_evil_good = tk.LabelFrame(master, text="Which team is Evil?")
        frame_evil_good.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.evil_var = tk.IntVar()
        # 1 => Team1 is Evil, 2 => Team2 is Evil
        radio_team1_evil = tk.Radiobutton(frame_evil_good, text="Team 1 is Evil", variable=self.evil_var, value=1)
        radio_team2_evil = tk.Radiobutton(frame_evil_good, text="Team 2 is Evil", variable=self.evil_var, value=2)

        radio_team1_evil.pack(anchor="w")
        radio_team2_evil.pack(anchor="w")

        # Winner selection
        frame_winner = tk.LabelFrame(master, text="Which team won?")
        frame_winner.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.winner_var = tk.IntVar()
        # 1 => Team1 won, 2 => Team2 won
        radio_team1_won = tk.Radiobutton(frame_winner, text="Team 1 won", variable=self.winner_var, value=1)
        radio_team2_won = tk.Radiobutton(frame_winner, text="Team 2 won", variable=self.winner_var, value=2)

        radio_team1_won.pack(anchor="w")
        radio_team2_won.pack(anchor="w")

        # Submit button
        btn_submit = tk.Button(master, text="Submit Game", command=self.submit_game)
        btn_submit.grid(row=2, column=0, columnspan=2, pady=10)

    def parse_team_input(self, text_widget):
        """
        Reads text from a Text widget, expects each line to be "Name Role".
        Returns a list of dicts: [ {"name": str, "role": str}, ... ]
        """
        lines = text_widget.get("1.0", tk.END).strip().split("\n")
        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)  # split into up to 2 parts
            if len(parts) == 1:
                # No role provided
                name = parts[0].strip()
                role = ""
            else:
                name, role = parts[0].strip(), parts[1].strip()

            parsed.append({"name": name, "role": role})
        return parsed

    def submit_game(self):
        """
        Gathers data from UI, updates Elo, and writes logs to Excel.
        """
        team1_data = self.parse_team_input(self.text_team1)
        team2_data = self.parse_team_input(self.text_team2)

        evil_selection = self.evil_var.get()
        winner_selection = self.winner_var.get()

        if evil_selection not in [1, 2] or winner_selection not in [1, 2]:
            messagebox.showwarning("Incomplete Selection", "Please indicate which team is Evil and which team won.")
            return

        # Determine team labels
        # If Team1 is Evil => Team1 = Evil, Team2 = Good. Otherwise vice versa.
        if evil_selection == 1:
            team1_team = "Evil"
            team2_team = "Good"
        else:
            team1_team = "Good"
            team2_team = "Evil"

        # Determine winning team
        if winner_selection == 1:
            winning_team = team1_team  # because Team1 won
        else:
            winning_team = team2_team

        # Combine them into a single "game" structure
        # e.g., "players": [{"name": X, "team": "Good"}, ...], "winning_team": "Good" or "Evil"
        game_players = []
        for p in team1_data:
            p["team"] = team1_team
            game_players.append(p)
        for p in team2_data:
            p["team"] = team2_team
            game_players.append(p)

        game_dict = {
            "players": game_players,
            "winning_team": winning_team
        }

        # Update Elo
        update_elo_for_game(game_dict)

        # Now store the game log to our in-memory (DataFrame approach).
        game_id = self.next_game_id
        self.next_game_id += 1

        game_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append per-player row to df_log
        new_rows = []
        for p in game_players:
            did_win = (p["team"] == winning_team)
            row = {
                "game_id": game_id,
                "date": game_date,
                "player_name": p["name"],
                "team": p["team"],
                "role": p["role"],
                "did_win": did_win
            }
            new_rows.append(row)

        # Convert to DataFrame and append to self.df_log
        df_new = pd.DataFrame(new_rows)
        self.df_log = pd.concat([self.df_log, df_new], ignore_index=True)

        # Save updated data to Excel
        save_game_log_to_excel(self.df_log)
        save_ratings_to_excel()

        # Clear the text boxes & selections
        self.text_team1.delete("1.0", tk.END)
        self.text_team2.delete("1.0", tk.END)
        self.evil_var.set(0)
        self.winner_var.set(0)

        messagebox.showinfo("Success", f"Game {game_id} logged. Elo updated.")


def main():
    root = tk.Tk()
    app = BotCEloApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
