import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------------------
# Constants and Defaults
# ---------------------------
DEFAULT_RATING = 1500
ELO_K_FACTOR = 32
PLAYERS_FILE = "players.json"
GAMELOG_FILE = "gamelog.json"

# ---------------------------
# Player Class Definition
# ---------------------------
class Player:
    def __init__(self, name):
        self.name = name
        self.current_rating = DEFAULT_RATING
        # Each rating history entry: { game_number, date, rating, overall_win_pct, good_win_pct, evil_win_pct }
        self.rating_history = []
        # Each game record: { game_number, date, team, role, win, rating_before, rating_after }
        self.game_history = []
        # Counters for recalculation
        self.games_overall = 0
        self.wins_overall = 0
        self.games_good = 0
        self.wins_good = 0
        self.games_evil = 0
        self.wins_evil = 0

    def record_game(self, game_number, date, team, role, win, rating_before, rating_after):
        record = {
            "game_number": game_number,
            "date": date,
            "team": team,
            "role": role,
            "win": win,
            "rating_before": rating_before,
            "rating_after": rating_after
        }
        self.game_history.append(record)
        self.games_overall += 1
        if win:
            self.wins_overall += 1
        if team == "Good":
            self.games_good += 1
            if win:
                self.wins_good += 1
        elif team == "Evil":
            self.games_evil += 1
            if win:
                self.wins_evil += 1
        if self.games_overall > 0:
            overall_pct = (self.wins_overall / self.games_overall) * 100
        else:
            overall_pct = None

        if self.games_good > 0:
            good_pct = (self.wins_good / self.games_good) * 100
        else:
            good_pct = None

        if self.games_evil > 0:
            evil_pct = (self.wins_evil / self.games_evil) * 100
        else:
            evil_pct = None
        self.rating_history.append({
            "game_number": game_number,
            "date": date,
            "rating": rating_after,
            "overall_win_pct": overall_pct,
            "good_win_pct": good_pct,
            "evil_win_pct": evil_pct
        })

    def to_dict(self):
        return {
            "name": self.name,
            "current_rating": self.current_rating,
            "rating_history": self.rating_history,
            "game_history": self.game_history
        }

    @staticmethod
    def from_dict(data):
        p = Player(data["name"])
        p.current_rating = data.get("current_rating", DEFAULT_RATING)
        p.rating_history = data.get("rating_history", [])
        p.game_history = data.get("game_history", [])
        return p

# ---------------------------
# Global Data
# ---------------------------
players = {}  # Dict: {player_name: Player instance}
game_log = []  # List of game records

# ---------------------------
# Data Persistence Functions
# ---------------------------
def load_data():
    global players, game_log
    if os.path.isfile(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r") as f:
            pdata = json.load(f)
        players = { p["name"]: Player.from_dict(p) for p in pdata }
    else:
        players = {}
    if os.path.isfile(GAMELOG_FILE):
        with open(GAMELOG_FILE, "r") as f:
            game_log = json.load(f)
    else:
        game_log = []

def save_data():
    with open(PLAYERS_FILE, "w") as f:
        json.dump([p.to_dict() for p in players.values()], f, indent=2)
    with open(GAMELOG_FILE, "w") as f:
        json.dump(game_log, f, indent=2)

# ---------------------------
# Elo Calculation Functions
# ---------------------------
def expected_score(ratingA, ratingB):
    return 1.0 / (1.0 + 10 ** ((ratingB - ratingA) / 400))

def recalc_all():
    """
    Recalculate all players’ ratings by replaying the game log.
    """
    for player in players.values():
        player.current_rating = DEFAULT_RATING
        player.rating_history = []
        player.game_history = []
        player.games_overall = 0
        player.wins_overall = 0
        player.games_good = 0
        player.wins_good = 0
        player.games_evil = 0
        player.wins_evil = 0

    sorted_games = sorted(game_log, key=lambda g: g["game_id"])
    for game in sorted_games:
        for p in game["players"]:
            name = p["name"]
            if name not in players:
                players[name] = Player(name)
        team_good = [p for p in game["players"] if p["team"] == "Good"]
        team_evil = [p for p in game["players"] if p["team"] == "Evil"]

        def team_average(team_list):
            if not team_list:
                return DEFAULT_RATING
            s = 0
            for p in team_list:
                s += players[p["name"]].current_rating
            return s / len(team_list)
        avg_good = team_average(team_good)
        avg_evil = team_average(team_evil)
        exp_good = expected_score(avg_good, avg_evil)
        exp_evil = 1.0 - exp_good

        if game["winning_team"] == "Good":
            result_good, result_evil = 1, 0
        else:
            result_good, result_evil = 0, 1

        for p in game["players"]:
            pl = players[p["name"]]
            rating_before = pl.current_rating
            if p["team"] == "Good":
                delta = ELO_K_FACTOR * (result_good - exp_good)
            else:
                delta = ELO_K_FACTOR * (result_evil - exp_evil)
            new_rating = rating_before + delta
            pl.current_rating = new_rating
            win = (p["team"] == game["winning_team"])
            pl.record_game(game["game_id"], game["date"], p["team"], p["role"], win, rating_before, new_rating)

def pct_to_str(value):
    """Convert a numeric percentage value to a formatted string or return 'N/A' if None."""
    if value is None:
        return "N/A"
    else:
        return f"{value:.1f}"

# ---------------------------
# UI Application
# ---------------------------
class EloTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Blood on the Clocktower Elo Tracker")
        # Configure the main window's grid
        master.rowconfigure(0, weight=0)  # submission frame (fixed)
        master.rowconfigure(1, weight=1)  # table frame (expandable)
        master.columnconfigure(0, weight=1)

        # ----- Top Frame: Submit New Game -----
        self.frame_submit = tk.LabelFrame(master, text="Submit New Game")
        self.frame_submit.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Inside the submission frame, we use grid too.
        # Team 1 Text Box
        self.text_team1 = tk.Text(self.frame_submit, width=40, height=8)
        self.text_team1.insert("end", "Enter Team 1 players (e.g., Alice_Jones Undertaker)\n")
        self.text_team1.grid(row=0, column=0, padx=5, pady=5)
        # Team 2 Text Box
        self.text_team2 = tk.Text(self.frame_submit, width=40, height=8)
        self.text_team2.insert("end", "Enter Team 2 players (e.g., Bob_Smith Imp)\n")
        self.text_team2.grid(row=0, column=1, padx=5, pady=5)
        # Radio buttons for Evil assignment
        frame_evil = tk.LabelFrame(self.frame_submit, text="Which team is Evil?")
        frame_evil.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.evil_var = tk.IntVar()
        tk.Radiobutton(frame_evil, text="Team 1 is Evil", variable=self.evil_var, value=1).pack(anchor="w")
        tk.Radiobutton(frame_evil, text="Team 2 is Evil", variable=self.evil_var, value=2).pack(anchor="w")
        # Radio buttons for Winner
        frame_winner = tk.LabelFrame(self.frame_submit, text="Which team won?")
        frame_winner.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.winner_var = tk.IntVar()
        tk.Radiobutton(frame_winner, text="Team 1 won", variable=self.winner_var, value=1).pack(anchor="w")
        tk.Radiobutton(frame_winner, text="Team 2 won", variable=self.winner_var, value=2).pack(anchor="w")
        # Submit Button
        btn_submit = tk.Button(self.frame_submit, text="Submit Game", command=self.submit_game)
        btn_submit.grid(row=2, column=0, columnspan=2, pady=10)

        # ----- Bottom Frame: Players Table -----
        self.frame_table = tk.LabelFrame(master, text="Players Elo & Win Percentages")
        self.frame_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_table.rowconfigure(0, weight=1)
        self.frame_table.columnconfigure(0, weight=1)
        # Create the Treeview using grid
        self.tree = ttk.Treeview(
            self.frame_table,
            columns=("Rank", "Name", "Rating", "Overall Win %", "Good Win %", "Evil Win %", "Games"),
            show="headings"
        )
        self.tree.heading("Rank", text="Rank")
        self.tree.column("Rank", width=50, anchor="center")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Overall Win %", text="Overall Win %")
        self.tree.heading("Good Win %", text="Good Win %")
        self.tree.heading("Evil Win %", text="Evil Win %")
        self.tree.heading("Games", text="Games Played")
        # Set column widths and anchors
        self.tree.column("Name", width=100, anchor="w")
        self.tree.column("Rating", width=80, anchor="center")
        self.tree.column("Overall Win %", width=100, anchor="center")
        self.tree.column("Good Win %", width=100, anchor="center")
        self.tree.column("Evil Win %", width=100, anchor="center")
        self.tree.column("Games", width=80, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        # Vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self.frame_table, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        # Bind double-click on Treeview rows
        self.tree.bind("<Double-1>", self.on_player_double_click)

        # Button to open the Edit Game Log window
        btn_edit = tk.Button(master, text="Edit Game Log", command=self.open_edit_window)
        btn_edit.grid(row=2, column=0, pady=5)

        # ----- Load Data and Refresh Table -----
        load_data()
        recalc_all()
        if game_log:
            self.next_game_id = max(g["game_id"] for g in game_log) + 1
        else:
            self.next_game_id = 1
        self.refresh_player_table()
    
    def open_edit_window(self):
        EditGameWindow(self.master)

    def parse_team_input(self, text_widget):
        lines = text_widget.get("1.0", "end").strip().split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            name = parts[0]
            role = parts[1] if len(parts) > 1 else ""
            result.append({"name": name, "role": role})
        return result

    def submit_game(self):
        team1 = self.parse_team_input(self.text_team1)
        team2 = self.parse_team_input(self.text_team2)
        evil_sel = self.evil_var.get()
        winner_sel = self.winner_var.get()
        if evil_sel not in [1, 2] or winner_sel not in [1, 2]:
            messagebox.showwarning("Incomplete Input", "Please select which team is Evil and which team won.")
            return
        if evil_sel == 1:
            team1_team = "Evil"
            team2_team = "Good"
        else:
            team1_team = "Good"
            team2_team = "Evil"
        winning_team = team1_team if winner_sel == 1 else team2_team

        game_id = self.next_game_id
        self.next_game_id += 1
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        players_in_game = []
        for p in team1:
            p["team"] = team1_team
            players_in_game.append(p)
        for p in team2:
            p["team"] = team2_team
            players_in_game.append(p)
        game_record = {
            "game_id": game_id,
            "date": date_str,
            "players": players_in_game,
            "winning_team": winning_team
        }
        game_log.append(game_record)
        recalc_all()
        self.refresh_player_table()
        save_data()

        # Clear inputs and selections
        self.text_team1.delete("1.0", "end")
        self.text_team2.delete("1.0", "end")
        self.evil_var.set(0)
        self.winner_var.set(0)
        messagebox.showinfo("Game Submitted", f"Game {game_id} has been logged and ratings updated.")

    def refresh_player_table(self):
        # Clear current contents in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Initialize ranking counter
        rank = 1
        
        # Sort players by current rating (highest first)
        for pname, player in sorted(players.items(), key=lambda x: x[1].current_rating, reverse=True):
            if player.rating_history:
                # Get the latest rating snapshot
                last = player.rating_history[-1]
                overall_pct = last.get("overall_win_pct")
                good_pct = last.get("good_win_pct")
                evil_pct = last.get("evil_win_pct")
            else:
                overall_pct, good_pct, evil_pct = None, None, None

            games_played = player.games_overall

            # Insert row with the following columns: Rank, Name, Rating, Overall Win %, Good Win %, Evil Win %, Games Played.
            self.tree.insert("", "end", iid=pname, values=(
                rank,
                pname,
                round(player.current_rating, 1),
                pct_to_str(overall_pct),
                pct_to_str(good_pct),
                pct_to_str(evil_pct),
                games_played
            ))
            rank += 1



    def on_player_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        pname = item
        if pname in players:
            self.show_player_graph(players[pname])

    def show_player_graph(self, player):
        import numpy as np
        if not player.rating_history:
            messagebox.showinfo("No Data", f"No rating history for {player.name}")
            return

        game_numbers = [entry["game_number"] for entry in player.rating_history]
        ratings = [entry["rating"] for entry in player.rating_history]
        overall = [np.nan if (entry["overall_win_pct"] is None) else entry["overall_win_pct"]
                for entry in player.rating_history]
        good = [np.nan if (entry["good_win_pct"] is None) else entry["good_win_pct"]
                for entry in player.rating_history]
        evil = [np.nan if (entry["evil_win_pct"] is None) else entry["evil_win_pct"]
                for entry in player.rating_history]

        fig, ax1 = plt.subplots()
        ax1.plot(game_numbers, ratings, marker='o', label="Rating", color="blue")
        ax1.set_xlabel("Game Number")
        ax1.set_ylabel("Rating", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")

        # Force integer x-ticks
        ax1.set_xticks(game_numbers)
        ax1.set_xticklabels([str(int(g)) for g in game_numbers])

        ax2 = ax1.twinx()
        ax2.plot(game_numbers, overall, marker='x', label="Overall Win %", color="red")
        ax2.plot(game_numbers, good, marker='x', label="Good Win %", color="green")
        ax2.plot(game_numbers, evil, marker='x', label="Evil Win %", color="purple")
        ax2.set_ylabel("Win Percentage", color="red")
        ax2.tick_params(axis="y", labelcolor="red")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc="best")

        plt.title(f"{player.name} - Rating & Win % History")
        plt.show()


# ---------------------------
# Edit Game Log Windows (Optional)
# ---------------------------
class EditGameWindow:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Edit Game Log")
        self.win.geometry("600x400")
        self.listbox = tk.Listbox(self.win, width=50)
        self.listbox.pack(padx=5, pady=5, side="left", fill="y")
        scrollbar = tk.Scrollbar(self.win, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        for game in sorted(game_log, key=lambda g: g["game_id"]):
            self.listbox.insert("end", f"Game {game['game_id']} - {game['date']}")
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(padx=5, pady=5, fill="both", expand=True)
        tk.Button(btn_frame, text="Edit Selected Game", command=self.edit_selected).pack(pady=5)
        tk.Button(btn_frame, text="Delete Selected Game", command=self.delete_selected).pack(pady=5)

    def get_selected_game_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def edit_selected(self):
        idx = self.get_selected_game_index()
        if idx is None:
            messagebox.showwarning("No Selection", "Please select a game to edit.")
            return
        game = sorted(game_log, key=lambda g: g["game_id"])[idx]
        EditSingleGameWindow(self.win, game)

    def delete_selected(self):
        global game_log
        idx = self.get_selected_game_index()
        if idx is None:
            messagebox.showwarning("No Selection", "Please select a game to delete.")
            return
        sorted_games = sorted(game_log, key=lambda g: g["game_id"])
        game_to_delete = sorted_games[idx]
        if messagebox.askyesno("Confirm Deletion", f"Delete Game {game_to_delete['game_id']}?"):
            game_log = [g for g in game_log if g["game_id"] != game_to_delete["game_id"]]
            recalc_all()
            save_data()
            messagebox.showinfo("Deleted", f"Game {game_to_delete['game_id']} deleted.")
            self.win.destroy()

class EditSingleGameWindow:
    def __init__(self, master, game):
        self.game = game
        self.win = tk.Toplevel(master)
        self.win.title(f"Edit Game {game['game_id']}")
        tk.Label(self.win, text="Team 1 (Name Role per line)").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.win, text="Team 2 (Name Role per line)").grid(row=0, column=1, padx=5, pady=5)
        self.text_team1 = tk.Text(self.win, width=40, height=8)
        self.text_team2 = tk.Text(self.win, width=40, height=8)
        self.text_team1.grid(row=1, column=0, padx=5, pady=5)
        self.text_team2.grid(row=1, column=1, padx=5, pady=5)
        team1_lines = []
        team2_lines = []
        if game["players"]:
            team_assignment = game["players"][0]["team"]
        else:
            team_assignment = "Good"
        for p in game["players"]:
            line = f"{p['name']} {p['role']}"
            if p["team"] == team_assignment:
                team1_lines.append(line)
            else:
                team2_lines.append(line)
        self.text_team1.insert("end", "\n".join(team1_lines))
        self.text_team2.insert("end", "\n".join(team2_lines))
        self.evil_var = tk.IntVar()
        frame_evil = tk.LabelFrame(self.win, text="Which team is Evil?")
        frame_evil.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        if team_assignment == "Evil":
            self.evil_var.set(1)
        else:
            self.evil_var.set(2)
        tk.Radiobutton(frame_evil, text="Team 1 is Evil", variable=self.evil_var, value=1).pack(anchor="w")
        tk.Radiobutton(frame_evil, text="Team 2 is Evil", variable=self.evil_var, value=2).pack(anchor="w")
        self.winner_var = tk.IntVar()
        frame_winner = tk.LabelFrame(self.win, text="Which team won?")
        frame_winner.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(frame_winner, text="Team 1 won", variable=self.winner_var, value=1).pack(anchor="w")
        tk.Radiobutton(frame_winner, text="Team 2 won", variable=self.winner_var, value=2).pack(anchor="w")
        self.winner_var.set(1)
        btn_save = tk.Button(self.win, text="Save Changes", command=self.save_changes)
        btn_save.grid(row=3, column=0, columnspan=2, pady=10)

    def parse_team_input(self, text_widget):
        lines = text_widget.get("1.0", "end").strip().split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            name = parts[0]
            role = parts[1] if len(parts) > 1 else ""
            result.append({"name": name, "role": role})
        return result

    def save_changes(self):
        team1 = self.parse_team_input(self.text_team1)
        team2 = self.parse_team_input(self.text_team2)
        evil_sel = self.evil_var.get()
        winner_sel = self.winner_var.get()
        if evil_sel not in [1,2] or winner_sel not in [1,2]:
            messagebox.showwarning("Incomplete Input", "Select which team is Evil and which won.")
            return
        if evil_sel == 1:
            team1_team = "Evil"
            team2_team = "Good"
        else:
            team1_team = "Good"
            team2_team = "Evil"
        winning_team = team1_team if winner_sel == 1 else team2_team
        players_in_game = []
        for p in team1:
            p["team"] = team1_team
            players_in_game.append(p)
        for p in team2:
            p["team"] = team2_team
            players_in_game.append(p)
        self.game["players"] = players_in_game
        self.game["winning_team"] = winning_team
        recalc_all()
        save_data()
        messagebox.showinfo("Saved", f"Game {self.game['game_id']} updated.")
        self.win.destroy()

# ---------------------------
# Main Execution
# ---------------------------
def main():
    root = tk.Tk()
    # Uncomment below to adjust default font after root creation if needed:
    # import tkinter.font as tkFont
    # default_font = tkFont.nametofont("TkDefaultFont")
    # default_font.configure(size=12)
    root.state('zoomed')
    app = EloTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
