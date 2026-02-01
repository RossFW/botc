import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform
import subprocess
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt
import io
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False
try:
    import AppKit
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False

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
    def __init__(self, name: str) -> None:
        self.name = name
        self.current_rating = DEFAULT_RATING
        # Each rating history entry: { game_number, date, rating, overall_win_pct, good_win_pct, evil_win_pct }
        self.rating_history: list[dict] = []
        # Each game record: { game_number, date, team, role, win, rating_before, rating_after }
        self.game_history: list[dict] = []
        # Counters for recalculation
        self.games_overall = 0
        self.wins_overall = 0
        self.games_good = 0
        self.wins_good = 0
        self.games_evil = 0
        self.wins_evil = 0

    def record_game(
        self,
        game_number: int,
        date: str,
        team: str,
        role: str,
        win: bool,
        rating_before: float,
        rating_after: float,
        *,
        initial_team: str | None = None,
        roles: list[str] | None = None,
    ) -> None:
        """
        Record a single game for this player.

        Parameters
        ----------
        game_number : int
            Sequential identifier for the game.
        date : str
            Datetime stamp of the game.
        team : str
            The player's final team at the end of the game ("Good" or "Evil").
        role : str
            The player's final role at the end of the game.
        win : bool
            Whether the player's final team won the game.
        rating_before : float
            Rating before the game.
        rating_after : float
            Rating after the game.
        initial_team : Optional[str]
            The player's starting team. Defaults to the final team if not provided.
        roles : Optional[List[str]]
            List of all roles played during the game. Defaults to [role] if not provided.
        """
        if roles is None:
            roles = [role]
        if initial_team is None:
            initial_team = team
        record = {
            "game_number": game_number,
            "date": date,
            "team": team,
            "role": role,
            "win": win,
            "rating_before": rating_before,
            "rating_after": rating_after,
            # Additional fields for tracking start and role history
            "initial_team": initial_team,
            "roles": roles,
        }
        self.game_history.append(record)
        # Update win/loss counters
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
        # Calculate percentages for history snapshot
        overall_pct = (self.wins_overall / self.games_overall) * 100 if self.games_overall > 0 else None
        good_pct = (self.wins_good / self.games_good) * 100 if self.games_good > 0 else None
        evil_pct = (self.wins_evil / self.games_evil) * 100 if self.games_evil > 0 else None
        self.rating_history.append(
            {
                "game_number": game_number,
                "date": date,
                "rating": rating_after,
                "overall_win_pct": overall_pct,
                "good_win_pct": good_pct,
                "evil_win_pct": evil_pct,
            }
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_rating": self.current_rating,
            "rating_history": self.rating_history,
            "game_history": self.game_history,
        }

    @staticmethod
    def from_dict(data: dict) -> "Player":
        p = Player(data["name"])
        p.current_rating = data.get("current_rating", DEFAULT_RATING)
        p.rating_history = data.get("rating_history", [])
        p.game_history = data.get("game_history", [])
        return p


# ---------------------------
# Global Data
# ---------------------------
players: dict[str, Player] = {}
game_log: list[dict] = []


# ---------------------------
# Data Persistence Functions
# ---------------------------
def load_data() -> None:
    """Load players and game log from JSON files if they exist."""
    global players, game_log
    if os.path.isfile(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        players = {p["name"]: Player.from_dict(p) for p in pdata}
    else:
        players = {}
    if os.path.isfile(GAMELOG_FILE):
        with open(GAMELOG_FILE, "r", encoding="utf-8") as f:
            game_log = json.load(f)
    else:
        game_log = []


def save_data() -> None:
    """Persist players and game log to JSON files."""
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in players.values()], f, indent=2)
    with open(GAMELOG_FILE, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=2)


# ---------------------------
# Elo Calculation Functions
# ---------------------------
def expected_score(ratingA: float, ratingB: float) -> float:
    return 1.0 / (1.0 + 10 ** ((ratingB - ratingA) / 400))


def recalc_all() -> None:
    """Recalculate all players’ ratings by replaying the game log."""
    # Reset all players
    for pl in players.values():
        pl.current_rating = DEFAULT_RATING
        pl.rating_history = []
        pl.game_history = []
        pl.games_overall = 0
        pl.wins_overall = 0
        pl.games_good = 0
        pl.wins_good = 0
        pl.games_evil = 0
        pl.wins_evil = 0

    # Replay games in chronological order
    sorted_games = sorted(game_log, key=lambda g: g["game_id"])
    for game in sorted_games:
        # Ensure all players exist
        for p in game["players"]:
            name = p["name"]
            if name not in players:
                players[name] = Player(name)
        # Partition players by final team
        team_good = [p for p in game["players"] if p["team"] == "Good"]
        team_evil = [p for p in game["players"] if p["team"] == "Evil"]

        def team_average(team_list: list[dict]) -> float:
            if not team_list:
                return DEFAULT_RATING
            return sum(players[p["name"]].current_rating for p in team_list) / len(team_list)

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
            win = p["team"] == game["winning_team"]
            # record final role for rating history
            pl.record_game(
                game["game_id"],
                game["date"],
                p["team"],
                p.get("role", ""),
                win,
                rating_before,
                new_rating,
                initial_team=p.get("initial_team"),
                roles=p.get("roles"),
            )


def pct_to_str(value: float | None) -> str:
    """Convert a numeric percentage value to a formatted string or return 'N/A' if None."""
    return f"{value:.1f}" if value is not None else "N/A"


# ---------------------------
# UI Application
# ---------------------------
class EloTrackerApp:
    def __init__(self, master: tk.Tk) -> None:
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
        self.text_team1.insert(
            "end", "Enter Team 1 players (e.g., Alice_Jones Undertaker)\n"
        )
        self.text_team1.grid(row=0, column=0, padx=5, pady=5)
        # Team 2 Text Box
        self.text_team2 = tk.Text(self.frame_submit, width=40, height=8)
        self.text_team2.insert(
            "end", "Enter Team 2 players (e.g., Bob_Smith Imp)\n"
        )
        self.text_team2.grid(row=0, column=1, padx=5, pady=5)
        # Radio buttons for Evil assignment
        frame_evil = tk.LabelFrame(self.frame_submit, text="Which team is Evil?")
        frame_evil.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.evil_var = tk.IntVar()
        tk.Radiobutton(frame_evil, text="Team 1 is Evil", variable=self.evil_var, value=1).pack(
            anchor="w"
        )
        tk.Radiobutton(frame_evil, text="Team 2 is Evil", variable=self.evil_var, value=2).pack(
            anchor="w"
        )
        # Radio buttons for Winner
        frame_winner = tk.LabelFrame(self.frame_submit, text="Which team won?")
        frame_winner.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.winner_var = tk.IntVar()
        tk.Radiobutton(frame_winner, text="Team 1 won", variable=self.winner_var, value=1).pack(
            anchor="w"
        )
        tk.Radiobutton(frame_winner, text="Team 2 won", variable=self.winner_var, value=2).pack(
            anchor="w"
        )
        # ----- Additional Inputs: Game Mode and Story Teller -----
        # Define available game modes
        # Import from centralized config - users can still type custom script names
        from botc_config import COMMON_SCRIPTS
        self.game_modes = COMMON_SCRIPTS
        # Game Mode selection
        frame_game_mode = tk.LabelFrame(self.frame_submit, text="Game Mode")
        frame_game_mode.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.game_mode_var = tk.StringVar(value=self.game_modes[0])
        # Combobox in normal state allows custom values to be typed in addition to selecting from the list
        self.dropdown_game_mode = ttk.Combobox(
            frame_game_mode,
            textvariable=self.game_mode_var,
            values=self.game_modes,
            state="normal",
        )
        self.dropdown_game_mode.pack(fill="x", padx=2, pady=2)
        # Story Teller input
        frame_story = tk.LabelFrame(self.frame_submit, text="Story Teller")
        frame_story.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.story_teller_entry = tk.Entry(frame_story)
        self.story_teller_entry.pack(fill="x", padx=2, pady=2)
        # Submit Button moved to row 3
        btn_submit = tk.Button(
            self.frame_submit, text="Submit Game", command=self.submit_game
        )
        btn_submit.grid(row=3, column=0, columnspan=2, pady=10)

        # ----- Bottom Frame: Players Table -----
        self.frame_table = tk.LabelFrame(master, text="Players Elo & Win Percentages")
        self.frame_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_table.rowconfigure(1, weight=1)
        self.frame_table.columnconfigure(0, weight=1)
        
        # Game range input frame
        range_frame = tk.Frame(self.frame_table)
        range_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tk.Label(range_frame, text="Game Range (e.g., 67-69 or leave blank):").pack(side=tk.LEFT, padx=5)
        self.game_range_entry = tk.Entry(range_frame, width=20)
        self.game_range_entry.pack(side=tk.LEFT, padx=5)
        self.game_range_entry.bind("<KeyRelease>", lambda e: self.refresh_player_table())
        tk.Button(range_frame, text="Clear Range", command=self.clear_game_range).pack(side=tk.LEFT, padx=5)
        
        # Create the Treeview using grid
        self.tree = ttk.Treeview(
            self.frame_table,
            columns=(
                "Rank",
                "Name",
                "Rating",
                "Delta Rating",
                "Overall Win %",
                "Good Win %",
                "Evil Win %",
                "Games",
            ),
            show="headings",
        )
        self.tree.heading("Rank", text="Rank")
        self.tree.column("Rank", width=50, anchor="center")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Delta Rating", text="Δ Rating")
        self.tree.heading("Overall Win %", text="Overall Win %")
        self.tree.heading("Good Win %", text="Good Win %")
        self.tree.heading("Evil Win %", text="Evil Win %")
        self.tree.heading("Games", text="Games Played")
        # Set column widths and anchors
        self.tree.column("Name", width=100, anchor="w")
        self.tree.column("Rating", width=80, anchor="center")
        self.tree.column("Delta Rating", width=90, anchor="center")
        self.tree.column("Overall Win %", width=100, anchor="center")
        self.tree.column("Good Win %", width=100, anchor="center")
        self.tree.column("Evil Win %", width=100, anchor="center")
        self.tree.column("Games", width=80, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        # Configure tags for delta rating colors (color blind friendly)
        self.tree.tag_configure("delta_positive", background="#b3d9ff")  # Light blue
        self.tree.tag_configure("delta_negative", background="#ffcc99")  # Light orange
        self.tree.tag_configure("delta_neutral", background="")
        
        # Vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(
            self.frame_table, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        # Bind double-click on Treeview rows to show graphs
        self.tree.bind("<Double-Button-1>", self.on_player_double_click)
        
        # Button frame for actions
        btn_frame = tk.Frame(master)
        btn_frame.grid(row=2, column=0, pady=5)
        btn_edit = tk.Button(btn_frame, text="Edit Game Log", command=self.open_edit_window)
        btn_edit.pack(side=tk.LEFT, padx=5)
        btn_screenshot = tk.Button(btn_frame, text="Copy Table as Image", command=self.copy_table_as_image)
        btn_screenshot.pack(side=tk.LEFT, padx=5)
        # ----- Load Data and Refresh Table -----
        load_data()
        recalc_all()
        if game_log:
            self.next_game_id = max(g["game_id"] for g in game_log) + 1
        else:
            self.next_game_id = 1
        self.refresh_player_table()

    def clear_game_range(self) -> None:
        """Clear the game range input field."""
        self.game_range_entry.delete(0, tk.END)
        self.refresh_player_table()
    
    def parse_game_range(self) -> tuple[int | None, int | None]:
        """
        Parse the game range input.
        Returns (start_game, end_game) or (None, None) if invalid/empty.
        Supports formats: "67-69", "67", "67-", "-69"
        """
        range_str = self.game_range_entry.get().strip()
        if not range_str:
            return None, None
        
        try:
            if "-" in range_str:
                parts = range_str.split("-")
                if len(parts) == 2:
                    start_str, end_str = parts[0].strip(), parts[1].strip()
                    start = int(start_str) if start_str else None
                    end = int(end_str) if end_str else None
                    return start, end
            else:
                # Single number
                game_num = int(range_str)
                return game_num, game_num
        except ValueError:
            return None, None
    
    def get_rating_delta(self, player: Player, start_game: int | None, end_game: int | None) -> float | None:
        """
        Calculate the rating delta for a player over a game range.
        Returns rating_after_end - rating_before_start, or None if range is invalid.
        """
        if start_game is None or end_game is None:
            return None
        
        if not player.rating_history:
            # Player has no history, can't calculate delta
            return None
        
        # Find rating before start_game (rating at the end of the last game before start_game)
        # If player hasn't played before start_game, use DEFAULT_RATING
        rating_before = DEFAULT_RATING
        for entry in player.rating_history:
            if entry["game_number"] < start_game:
                rating_before = entry["rating"]
            else:
                # We've reached games >= start_game, stop looking
                break
        
        # Find rating after end_game (rating at the end of end_game)
        # We need to find the rating at the end of end_game specifically
        rating_after = None
        for entry in player.rating_history:
            if entry["game_number"] == end_game:
                rating_after = entry["rating"]
                break
            elif entry["game_number"] > end_game:
                # We've passed end_game, use the last rating before it
                break
        
        # If we didn't find a rating at end_game, try to find the closest one <= end_game
        if rating_after is None:
            for entry in reversed(player.rating_history):
                if entry["game_number"] <= end_game:
                    rating_after = entry["rating"]
                    break
        
        # If player didn't play up to end_game, can't calculate delta
        if rating_after is None:
            return None
        
        return rating_after - rating_before
    
    def open_edit_window(self) -> None:
        EditGameWindow(self.master)

    @staticmethod
    def _standardize_role(role_part: str) -> str:
        """
        Convert a raw role string to a standardized form.
        Handles underscores and capitalization so that 'witch' and 'Witch' are treated the same.
        """
        if not role_part:
            return ""
        # split on underscores, capitalize first letter of each segment
        segments = role_part.split("_")
        standardized_segments: list[str] = []
        for seg in segments:
            if seg:
                # Preserve apostrophes and other punctuation, but standardize case
                standardized_segments.append(seg[0].upper() + seg[1:].lower())
            else:
                standardized_segments.append(seg)
        return "_".join(standardized_segments)

    def parse_team_input(self, text_widget: tk.Text) -> list[dict]:
        """
        Parse a multi-line text input for team players.
        Each line is expected to be of the form:
          Name Role [InitialTeam]
        - Name: player name (underscores for spaces)
        - Role: role string; if multiple roles, separate with '+' (e.g., Virgin+Witch)
        - InitialTeam (optional): starting team, or a start->end pattern (e.g., Good->Evil)
        Returns a list of dictionaries with name, roles (list), role (final), and initial_team.
        """
        lines = text_widget.get("1.0", "end").strip().split("\n")
        result: list[dict] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            role_str = parts[1] if len(parts) >= 2 else ""
            team_hint = parts[2] if len(parts) >= 3 else None
            # Process roles: split on '+', then standardize each
            if role_str:
                raw_roles = role_str.split("+")
            else:
                raw_roles = [""]
            roles: list[str] = []
            for rp in raw_roles:
                roles.append(self._standardize_role(rp))
            final_role = roles[-1] if roles else ""
            # Process team hint: only initial team is captured here
            initial_team = None
            if team_hint:
                if "->" in team_hint:
                    # only store start team; end team will be assigned from radio buttons
                    initial_team = team_hint.split("->")[0].capitalize()
                else:
                    initial_team = team_hint.capitalize()
            result.append(
                {
                    "name": name,
                    "roles": roles,
                    "role": final_role,
                    "initial_team": initial_team,
                }
            )
        return result

    def submit_game(self) -> None:
        # Collect team inputs
        team1 = self.parse_team_input(self.text_team1)
        team2 = self.parse_team_input(self.text_team2)
        evil_sel = self.evil_var.get()
        winner_sel = self.winner_var.get()
        if evil_sel not in [1, 2] or winner_sel not in [1, 2]:
            messagebox.showwarning(
                "Incomplete Input",
                "Please select which team is Evil and which team won.",
            )
            return
        # Determine final team labels
        if evil_sel == 1:
            team1_team = "Evil"
            team2_team = "Good"
        else:
            team1_team = "Good"
            team2_team = "Evil"
        winning_team = team1_team if winner_sel == 1 else team2_team
        # Determine game mode and story teller
        game_mode = self.game_mode_var.get()
        story_teller = self.story_teller_entry.get().strip()
        # Assign teams and ensure initial_team defaults
        players_in_game: list[dict] = []
        for p in team1:
            # final team assignment
            p["team"] = team1_team
            # default initial_team if not provided
            if not p.get("initial_team"):
                p["initial_team"] = team1_team
            players_in_game.append(p)
        for p in team2:
            p["team"] = team2_team
            if not p.get("initial_team"):
                p["initial_team"] = team2_team
            players_in_game.append(p)
        # Build game record
        game_id = self.next_game_id
        self.next_game_id += 1
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        game_record = {
            "game_id": game_id,
            "date": date_str,
            "players": players_in_game,
            "winning_team": winning_team,
            "game_mode": game_mode,
            "story_teller": story_teller,
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
        self.game_mode_var.set(self.game_modes[0])
        self.story_teller_entry.delete(0, "end")
        messagebox.showinfo(
            "Game Submitted", f"Game {game_id} has been logged and ratings updated."
        )

    def refresh_player_table(self) -> None:
        # Clear current contents in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Initialize ranking counter
        rank = 1
        # Parse game range
        start_game, end_game = self.parse_game_range()
        
        # Sort players by current rating (highest first)
        for pname, player in sorted(
            players.items(), key=lambda x: x[1].current_rating, reverse=True
        ):
            if player.rating_history:
                # Get the latest rating snapshot
                last = player.rating_history[-1]
                overall_pct = last.get("overall_win_pct")
                good_pct = last.get("good_win_pct")
                evil_pct = last.get("evil_win_pct")
            else:
                overall_pct, good_pct, evil_pct = None, None, None
            games_played = player.games_overall

            if games_played < 5:
                continue

            # Calculate delta rating
            delta = self.get_rating_delta(player, start_game, end_game)
            if delta is not None:
                delta_str = f"{delta:+.1f}"
                # Determine tag based on delta value
                if delta > 0:
                    tag = "delta_positive"
                elif delta < 0:
                    tag = "delta_negative"
                else:
                    tag = "delta_neutral"
            else:
                delta_str = "-"
                tag = "delta_neutral"
            
            # Insert row with the following columns: Rank, Name, Rating, Delta Rating, Overall Win %, Good Win %, Evil Win %, Games Played.
            self.tree.insert(
                "",
                "end",
                iid=pname,
                values=(
                    rank,
                    pname,
                    round(player.current_rating, 1),
                    delta_str,
                    pct_to_str(overall_pct),
                    pct_to_str(good_pct),
                    pct_to_str(evil_pct),
                    games_played,
                ),
                tags=(tag,),
            )
            rank += 1

    def on_player_double_click(self, event: tk.Event) -> None:
        item = self.tree.identify("item", event.x, event.y)
        if not item:
            return
        pname = item
        if pname in players:
            self.show_player_graph(players[pname])

    def copy_table_as_image(self) -> None:
        """Copy the table as an image to clipboard (if pyperclip available) or save to file."""
        if not HAS_PIL:
            messagebox.showerror(
                "Missing Dependency",
                "PIL/Pillow is required for image generation.\n"
                "Please install it with: pip install Pillow"
            )
            return
        try:
            # Get all table data with tags for delta coloring
            rows = []
            row_tags = []  # Store tags for each row to determine delta column color
            # Get headers
            headers = ["Rank", "Name", "Rating", "Δ Rating", "Overall Win %", "Good Win %", "Evil Win %", "Games"]
            rows.append(headers)
            row_tags.append([])  # No tags for header
            
            # Get all rows
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, "values")
                tags = self.tree.item(item_id, "tags")
                rows.append(list(values))
                row_tags.append(tags)
            
            if not rows:
                messagebox.showwarning("No Data", "No data to copy.")
                return
            
            # Calculate image dimensions
            num_cols = len(headers)
            num_rows = len(rows)
            
            # Font sizes for phone readability
            header_font_size = 18
            cell_font_size = 16
            padding = 10
            row_height = 35
            col_widths = [60, 120, 80, 90, 110, 110, 110, 80]  # Adjusted for readability
            
            # Calculate total dimensions
            total_width = sum(col_widths) + padding * (num_cols + 1)
            total_height = row_height * num_rows + padding * (num_rows + 1) + 40  # Extra space for title
            
            # Create image
            img = Image.new("RGB", (total_width, total_height), color="white")
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fallback to default
            try:
                header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", header_font_size)
                cell_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", cell_font_size)
            except:
                try:
                    header_font = ImageFont.truetype("arial.ttf", header_font_size)
                    cell_font = ImageFont.truetype("arial.ttf", cell_font_size)
                except:
                    header_font = ImageFont.load_default()
                    cell_font = ImageFont.load_default()
            
            # Draw title
            title = "Blood on the Clocktower Elo Tracker"
            title_bbox = draw.textbbox((0, 0), title, font=header_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (total_width - title_width) // 2
            draw.text((title_x, padding), title, fill="black", font=header_font)
            
            y_offset = padding * 2 + 30
            
            # Draw table
            for row_idx, row_data in enumerate(rows):
                x_offset = padding
                is_header = row_idx == 0
                font = header_font if is_header else cell_font
                
                for col_idx, cell_text in enumerate(row_data):
                    cell_width = col_widths[col_idx]
                    
                    # Background color for entire row based on delta
                    if is_header:
                        bg_color = (240, 240, 240)  # Light gray for header
                    elif row_idx < len(row_tags):
                        # Get the tag for this row to determine color
                        tags = row_tags[row_idx]
                        if "delta_positive" in tags:
                            bg_color = (179, 217, 255)  # Light blue for entire row
                        elif "delta_negative" in tags:
                            bg_color = (255, 204, 153)  # Light orange for entire row
                        else:
                            bg_color = (255, 255, 255)  # White
                    else:
                        bg_color = (255, 255, 255)  # White
                    
                    # Draw cell background
                    draw.rectangle(
                        [x_offset, y_offset, x_offset + cell_width, y_offset + row_height],
                        fill=bg_color,
                        outline="black",
                        width=1
                    )
                    
                    # Draw cell text
                    text_color = "black"
                    # Center align for numeric columns
                    if col_idx in [0, 2, 3, 4, 5, 6, 7]:  # Numeric columns
                        text_bbox = draw.textbbox((0, 0), str(cell_text), font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_x = x_offset + (cell_width - text_width) // 2
                    else:  # Left align for name
                        text_x = x_offset + 5
                    
                    text_y = y_offset + (row_height - header_font_size) // 2
                    draw.text((text_x, text_y), str(cell_text), fill=text_color, font=font)
                    
                    x_offset += cell_width + padding
                
                y_offset += row_height + padding
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            img_data = img_bytes.read()
            
            # Try to copy to clipboard (macOS preferred method)
            clipboard_success = False
            error_msg = None
            
            # Method 1: Use AppKit on macOS (most reliable)
            if platform.system() == "Darwin" and HAS_APPKIT:
                try:
                    pasteboard = AppKit.NSPasteboard.generalPasteboard()
                    pasteboard.clearContents()
                    ns_image = AppKit.NSImage.alloc().initWithData_(img_data)
                    pasteboard.writeObjects_([ns_image])
                    clipboard_success = True
                except Exception as e:
                    error_msg = str(e)
            
            # Method 2: Use AppleScript on macOS (fallback)
            if not clipboard_success and platform.system() == "Darwin":
                try:
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(img_data)
                        tmp_path = tmp_file.name
                    
                    # Use AppleScript to copy image to clipboard
                    script = f'''
                    set the clipboard to (read file POSIX file "{tmp_path}" as «class PNGf»)
                    '''
                    result = subprocess.run(
                        ['osascript', '-e', script],
                        capture_output=True,
                        text=True
                    )
                    
                    # Clean up temp file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    
                    if result.returncode == 0:
                        clipboard_success = True
                    else:
                        error_msg = result.stderr
                except Exception as e:
                    if error_msg is None:
                        error_msg = str(e)
            
            # Show success message
            if clipboard_success:
                messagebox.showinfo(
                    "Image Copied!",
                    "Table image copied to clipboard!\n"
                    "You can now paste it (Cmd+V) into any app."
                )
            else:
                # Fallback: save to file
                filename = "botc_table_screenshot.png"
                with open(filename, "wb") as f:
                    f.write(img_data)
                error_text = f"Table image saved as '{filename}' in the current directory."
                if error_msg:
                    error_text += f"\n\nNote: Could not copy to clipboard ({error_msg})"
                elif platform.system() != "Darwin":
                    error_text += "\n\nNote: Clipboard copying is optimized for macOS."
                messagebox.showinfo("Image Saved", error_text)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create image: {e}")
    
    def show_player_graph(self, player: Player) -> None:
        import numpy as np
        if not player.rating_history:
            messagebox.showinfo("No Data", f"No rating history for {player.name}")
            return
        game_numbers = [entry["game_number"] for entry in player.rating_history]
        ratings = [entry["rating"] for entry in player.rating_history]
        overall = [
            np.nan if (entry["overall_win_pct"] is None) else entry["overall_win_pct"]
            for entry in player.rating_history
        ]
        good = [
            np.nan if (entry["good_win_pct"] is None) else entry["good_win_pct"]
            for entry in player.rating_history
        ]
        evil = [
            np.nan if (entry["evil_win_pct"] is None) else entry["evil_win_pct"]
            for entry in player.rating_history
        ]
        fig, ax1 = plt.subplots()
        ax1.plot(game_numbers, ratings, marker="o", label="Rating", color="blue")
        ax1.set_xlabel("Game Number")
        ax1.set_ylabel("Rating", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        # Force integer x-ticks
        ax1.set_xticks(game_numbers)
        ax1.set_xticklabels([str(int(g)) for g in game_numbers])
        ax2 = ax1.twinx()
        ax2.plot(game_numbers, overall, marker="x", label="Overall Win %", color="red")
        ax2.plot(game_numbers, good, marker="x", label="Good Win %", color="green")
        ax2.plot(game_numbers, evil, marker="x", label="Evil Win %", color="purple")
        ax2.set_ylabel("Win Percentage", color="red")
        ax2.tick_params(axis="y", labelcolor="red")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc="best")
        plt.title(f"{player.name} - Rating & Win % History")
        plt.show()


# ---------------------------
# Edit Game Log Windows
# ---------------------------
class EditGameWindow:
    def __init__(self, master: tk.Tk) -> None:
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
            self.listbox.insert(
                "end", f"Game {game['game_id']} - {game['date']}"
            )
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(padx=5, pady=5, fill="both", expand=True)
        tk.Button(btn_frame, text="Edit Selected Game", command=self.edit_selected).pack(
            pady=5
        )
        tk.Button(btn_frame, text="Delete Selected Game", command=self.delete_selected).pack(
            pady=5
        )

    def get_selected_game_index(self) -> int | None:
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def edit_selected(self) -> None:
        idx = self.get_selected_game_index()
        if idx is None:
            messagebox.showwarning("No Selection", "Please select a game to edit.")
            return
        game = sorted(game_log, key=lambda g: g["game_id"])[idx]
        EditSingleGameWindow(self.win, game)

    def delete_selected(self) -> None:
        global game_log
        idx = self.get_selected_game_index()
        if idx is None:
            messagebox.showwarning("No Selection", "Please select a game to delete.")
            return
        sorted_games = sorted(game_log, key=lambda g: g["game_id"])
        game_to_delete = sorted_games[idx]
        if messagebox.askyesno(
            "Confirm Deletion", f"Delete Game {game_to_delete['game_id']}?"
        ):
            game_log = [g for g in game_log if g["game_id"] != game_to_delete["game_id"]]
            recalc_all()
            save_data()
            messagebox.showinfo(
                "Deleted", f"Game {game_to_delete['game_id']} deleted."
            )
            self.win.destroy()


class EditSingleGameWindow:
    def __init__(self, master: tk.Tk, game: dict) -> None:
        self.game = game
        self.win = tk.Toplevel(master)
        self.win.title(f"Edit Game {game['game_id']}")
        tk.Label(self.win, text="Team 1 (Name Role per line)").grid(
            row=0, column=0, padx=5, pady=5
        )
        tk.Label(self.win, text="Team 2 (Name Role per line)").grid(
            row=0, column=1, padx=5, pady=5
        )
        self.text_team1 = tk.Text(self.win, width=40, height=8)
        self.text_team2 = tk.Text(self.win, width=40, height=8)
        self.text_team1.grid(row=1, column=0, padx=5, pady=5)
        self.text_team2.grid(row=1, column=1, padx=5, pady=5)
        # reconstruct team lists from game players
        team1_lines: list[str] = []
        team2_lines: list[str] = []
        # Determine which final team is assigned to team1
        if game["players"]:
            team_assignment = game["players"][0]["team"]
        else:
            team_assignment = "Good"
        for p in game["players"]:
            # reconstruct roles display
            role_display = "+".join(p.get("roles", [p.get("role", "")]))
            # reconstruct team hint for initial team if available and changed
            team_hint = ""
            initial = p.get("initial_team")
            final_team = p.get("team")
            if initial:
                if final_team and initial != final_team:
                    team_hint = f" {initial}->{final_team}"
                else:
                    team_hint = f" {initial}"
            line = f"{p['name']} {role_display}{team_hint}"
            if p["team"] == team_assignment:
                team1_lines.append(line)
            else:
                team2_lines.append(line)
        self.text_team1.insert("end", "\n".join(team1_lines))
        self.text_team2.insert("end", "\n".join(team2_lines))
        # Evil / Good assignment
        self.evil_var = tk.IntVar()
        frame_evil = tk.LabelFrame(self.win, text="Which team is Evil?")
        frame_evil.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        # set default based on which team in original game log is evil
        if team_assignment == "Evil":
            self.evil_var.set(1)
        else:
            self.evil_var.set(2)
        tk.Radiobutton(
            frame_evil, text="Team 1 is Evil", variable=self.evil_var, value=1
        ).pack(anchor="w")
        tk.Radiobutton(
            frame_evil, text="Team 2 is Evil", variable=self.evil_var, value=2
        ).pack(anchor="w")
        # Winner assignment
        self.winner_var = tk.IntVar()
        frame_winner = tk.LabelFrame(self.win, text="Which team won?")
        frame_winner.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(
            frame_winner, text="Team 1 won", variable=self.winner_var, value=1
        ).pack(anchor="w")
        tk.Radiobutton(
            frame_winner, text="Team 2 won", variable=self.winner_var, value=2
        ).pack(anchor="w")
        # set default winner based on original game record
        if game.get("winning_team", "Good") == team_assignment:
            self.winner_var.set(1)
        else:
            self.winner_var.set(2)
        # Save button
        btn_save = tk.Button(self.win, text="Save Changes", command=self.save_changes)
        btn_save.grid(row=3, column=0, columnspan=2, pady=10)

    def parse_team_input(self, text_widget: tk.Text) -> list[dict]:
        """Parse text lines for a team in the edit window using the same rules as the main form."""
        lines = text_widget.get("1.0", "end").strip().split("\n")
        result: list[dict] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            role_str = parts[1] if len(parts) >= 2 else ""
            team_hint = parts[2] if len(parts) >= 3 else None
            # roles
            if role_str:
                raw_roles = role_str.split("+")
            else:
                raw_roles = [""]
            roles: list[str] = []
            for rp in raw_roles:
                roles.append(EloTrackerApp._standardize_role(rp))
            final_role = roles[-1] if roles else ""
            # initial team
            initial_team = None
            if team_hint:
                if "->" in team_hint:
                    initial_team = team_hint.split("->")[0].capitalize()
                else:
                    initial_team = team_hint.capitalize()
            result.append(
                {
                    "name": name,
                    "roles": roles,
                    "role": final_role,
                    "initial_team": initial_team,
                }
            )
        return result

    def save_changes(self) -> None:
        # Parse inputs
        team1 = self.parse_team_input(self.text_team1)
        team2 = self.parse_team_input(self.text_team2)
        evil_sel = self.evil_var.get()
        winner_sel = self.winner_var.get()
        if evil_sel not in [1, 2] or winner_sel not in [1, 2]:
            messagebox.showwarning(
                "Incomplete Input", "Select which team is Evil and which won."
            )
            return
        if evil_sel == 1:
            team1_team = "Evil"
            team2_team = "Good"
        else:
            team1_team = "Good"
            team2_team = "Evil"
        winning_team = team1_team if winner_sel == 1 else team2_team
        players_in_game: list[dict] = []
        for p in team1:
            p["team"] = team1_team
            if not p.get("initial_team"):
                p["initial_team"] = team1_team
            players_in_game.append(p)
        for p in team2:
            p["team"] = team2_team
            if not p.get("initial_team"):
                p["initial_team"] = team2_team
            players_in_game.append(p)
        # Update game record
        self.game["players"] = players_in_game
        self.game["winning_team"] = winning_team
        # game_mode and story_teller remain unchanged on edit
        recalc_all()
        save_data()
        messagebox.showinfo(
            "Saved", f"Game {self.game['game_id']} updated."
        )
        self.win.destroy()


# ---------------------------
# Main Execution
# ---------------------------
def main() -> None:
    root = tk.Tk()
    # Optionally set window to maximized/zoomed if supported
    try:
        root.state("zoomed")
    except Exception:
        pass
    app = EloTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()