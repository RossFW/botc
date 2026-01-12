"""
Analytics Dashboard for Blood on the Clocktower (BOTC) games by Storyteller.

This standalone script reads the existing ``gamelog.json`` produced by the
``botc_elo.py`` application and surfaces aggregated statistics for games
run by a specific storyteller. The storyteller can be selected via a search
interface.

Features
--------
* **Storyteller selection:** Search and select any storyteller from the game log
* **Overall statistics:** Total games, Good vs Evil winrates for the selected storyteller
* **Script statistics:** breakdown of games played, Good and Evil wins and
  win percentages for each script. Scripts are categorised into
  ``Normal`` or ``Teensyville`` depending on whether they are one of the
  core scripts (*Trouble Brewing*, *Bad Moon Rising*, *Sects & Violets* or
  *Trouble in Violets*) or something else. Totals for the two categories
  are also displayed.

* **Character statistics:** for each script (or across all scripts or by
  category) you can view how often each character appeared and how often
  the character's team won. This helps identify which roles tend to be
  associated with victories or defeats.

* **Player statistics:** aggregated win rates for each player across all
  games run by the selected storyteller. For every player you can see their total games,
  wins, Good games/wins, Evil games/wins and the corresponding win
  percentages. Double‑clicking on a player row opens a detail window
  showing per‑script win rates as well as the player's personal record
  with each role.

To run the dashboard simply execute this file in the same directory as
``gamelog.json``:

```
python3 storyteller_analytics.py
```

This will open a Tkinter window with storyteller selection and tabs for the different analytics views.
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import ttk

from typing import Dict, List, Any, Set

# Import centralized configuration
from botc_config import categorize_script, normalize_script_name


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Names of JSON files; these must exist in the working directory. Only
# ``gamelog.json`` is required – ``players.json`` is not needed for the
# analytics since all statistics are derived directly from the game log.
GAMELOG_FILE = "gamelog.json"


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def load_gamelog() -> List[Dict[str, Any]]:
    """Load the game log from JSON. Returns an empty list if missing."""
    if not os.path.isfile(GAMELOG_FILE):
        return []
    with open(GAMELOG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # Ensure the list is sorted by game_id for reproducibility
            data.sort(key=lambda g: g.get("game_id", 0))
            return data
        except Exception:
            return []


def normalize_name(name: str) -> str:
    """Return a lowercase stripped version of a name for comparison."""
    return (name or "").strip().lower()


def extract_storytellers(games: List[Dict[str, Any]]) -> Set[str]:
    """Extract all unique storyteller names from the game log."""
    storytellers: Set[str] = set()
    for game in games:
        st_val = game.get("story_teller", "")
        if st_val:
            # Split on '+' to handle multiple storytellers
            parts = [p.strip() for p in st_val.split('+') if p.strip()]
            storytellers.update(parts)
    return storytellers


def has_storyteller(game: Dict[str, Any], storyteller_name: str) -> bool:
    """Check if a game was storytold by the given storyteller (case-insensitive, partial match)."""
    st_val = game.get("story_teller", "")
    if not st_val:
        return False
    # Split on '+' to handle multiple storytellers
    parts = [normalize_name(p.strip()) for p in st_val.split('+') if p.strip()]
    target = normalize_name(storyteller_name)
    # Check if any storyteller name contains the target (for partial matching)
    return any(target in part or part in target for part in parts)


# ---------------------------------------------------------------------------
# Analytics classes
# ---------------------------------------------------------------------------

class StorytellerAnalytics:
    """
    Compute statistics for games run by a specific storyteller.

    Parameters
    ----------
    games : list of dict
        The entire list of games from ``gamelog.json``. Only games whose
        ``story_teller`` field matches the target storyteller are considered.
    storyteller_name : str
        The name of the storyteller to analyze.

    Attributes
    ----------
    storyteller_name : str
        The name of the storyteller being analyzed.
    games : list of dict
        Filtered list of games run by the target storyteller.
    script_stats : dict
        Mapping of script name to a dict with ``category``, ``games``,
        ``good_wins`` and ``evil_wins`` for that script.
    category_totals : dict
        Totals for each category (``Normal`` and ``Teensyville``).
    player_stats : dict
        Mapping of player name to aggregated statistics across all games.
    """

    def __init__(self, games: List[Dict[str, Any]], storyteller_name: str) -> None:
        self.storyteller_name = storyteller_name
        # Filter games to include those where the storyteller list contains the target
        # storyteller.  A game may have multiple storytellers separated by '+' (e.g.
        # "Marlie_Horewitz+Matan_Diamond").  We treat the game as belonging to the
        # target storyteller if one of the names matches (case-insensitive, partial match).
        self.games: List[Dict[str, Any]] = [
            g for g in games if has_storyteller(g, storyteller_name)
        ]
        self.script_stats: Dict[str, Dict[str, Any]] = {}
        self.category_totals: Dict[str, Dict[str, Any]] = {}
        self.player_stats: Dict[str, Dict[str, Any]] = {}
        self._compute_script_stats()
        self._compute_player_stats()

    def _compute_script_stats(self) -> None:
        """Populate per‑script statistics and category totals."""
        stats: Dict[str, Dict[str, Any]] = {}
        # Count per script
        for game in self.games:
            script = game.get("game_mode", "") or ""
            cat = categorize_script(script)
            entry = stats.setdefault(
                script,
                {
                    "category": cat,
                    "games": 0,
                    "good_wins": 0,
                    "evil_wins": 0,
                },
            )
            entry["games"] += 1
            if game.get("winning_team") == "Good":
                entry["good_wins"] += 1
            else:
                entry["evil_wins"] += 1
        # Store script stats
        self.script_stats = stats
        # Compute category totals
        totals: Dict[str, Dict[str, Any]] = {
            "Normal": {"games": 0, "good_wins": 0, "evil_wins": 0},
            "Teensyville": {"games": 0, "good_wins": 0, "evil_wins": 0},
        }
        for script, entry in stats.items():
            cat = entry["category"]
            totals[cat]["games"] += entry["games"]
            totals[cat]["good_wins"] += entry["good_wins"]
            totals[cat]["evil_wins"] += entry["evil_wins"]
        self.category_totals = totals

    def _compute_player_stats(self) -> None:
        """Build aggregated statistics for each player across filtered games."""
        ps: Dict[str, Dict[str, Any]] = {}
        for game in self.games:
            winning_team = game.get("winning_team")
            script = game.get("game_mode", "") or ""
            for p in game.get("players", []):
                name = p.get("name", "").strip()
                if not name:
                    continue
                team = p.get("team")
                # Set default structure
                entry = ps.setdefault(
                    name,
                    {
                        "games": 0,
                        "wins": 0,
                        "good_games": 0,
                        "good_wins": 0,
                        "evil_games": 0,
                        "evil_wins": 0,
                        "scripts": {},  # per‑script counts
                        "roles": {},  # role counts across all games
                    },
                )
                entry["games"] += 1
                # Win
                if team == winning_team:
                    entry["wins"] += 1
                # Alignment breakdown
                if team == "Good":
                    entry["good_games"] += 1
                    if team == winning_team:
                        entry["good_wins"] += 1
                elif team == "Evil":
                    entry["evil_games"] += 1
                    if team == winning_team:
                        entry["evil_wins"] += 1
                # Per‑script counts
                s_entry = entry["scripts"].setdefault(
                    script,
                    {"games": 0, "wins": 0},
                )
                s_entry["games"] += 1
                if team == winning_team:
                    s_entry["wins"] += 1
                # Role counts – include all roles in the history if available
                # Each player record in the game may have ``roles`` list; fall
                # back to final role if missing.
                roles_list = p.get("roles") or [p.get("role")]
                if roles_list:
                    for role in roles_list:
                        r_entry = entry["roles"].setdefault(
                            role,
                            {"games": 0, "wins": 0},
                        )
                        r_entry["games"] += 1
                        if team == winning_team:
                            r_entry["wins"] += 1
        self.player_stats = ps


# ---------------------------------------------------------------------------
# Tkinter UI
# ---------------------------------------------------------------------------

class AnalyticsUI:
    """Main window for displaying analytics across multiple tabs."""

    def __init__(self, root: tk.Tk, all_games: List[Dict[str, Any]]) -> None:
        self.root = root
        self.all_games = all_games
        self.analytics: StorytellerAnalytics | None = None
        
        # Extract all unique storytellers
        self.all_storytellers = sorted(extract_storytellers(all_games))
        
        root.title("BOTC Storyteller Analytics")
        root.geometry("1000x700")
        
        # Storyteller selection frame at the top
        selection_frame = tk.Frame(root)
        selection_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(selection_frame, text="Storyteller:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        # Combobox for selection (editable with autocomplete)
        self.storyteller_var = tk.StringVar()
        self.combobox = ttk.Combobox(
            selection_frame,
            textvariable=self.storyteller_var,
            values=self.all_storytellers,
            state="normal",  # Make it editable
            width=40,
            font=("Arial", 11)
        )
        self.combobox.pack(side="left", padx=5)
        self.combobox.bind("<<ComboboxSelected>>", lambda e: self._on_storyteller_selected())
        self.combobox.bind("<KeyRelease>", self._on_search_change)
        self.combobox.bind("<Return>", lambda e: self._select_storyteller())
        
        # Summary frame for overall stats
        self.summary_frame = tk.LabelFrame(root, text="Storyteller Summary", font=("Arial", 11, "bold"))
        self.summary_frame.pack(fill="x", padx=5, pady=5)
        
        self.summary_labels = {}
        for i, label_text in enumerate([
            "Storyteller: Not selected",
            "Total Games: 0",
            "Good Wins: 0 (0.0%)",
            "Evil Wins: 0 (0.0%)"
        ]):
            lbl = tk.Label(self.summary_frame, text=label_text, font=("Arial", 10))
            lbl.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=5)
            self.summary_labels[i] = lbl
        
        # Build notebook with three tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        
        # Scripts tab
        self.frame_scripts = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_scripts, text="Scripts")
        
        # Characters tab
        self.frame_characters = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_characters, text="Characters")
        
        # Players tab
        self.frame_players = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_players, text="Players")
        
        # Initialize empty tabs
        self._build_scripts_tab(self.frame_scripts)
        self._build_characters_tab(self.frame_characters)
        self._build_players_tab(self.frame_players)

    def _on_search_change(self, event=None) -> None:
        """Filter combobox options based on search text as user types."""
        search_text = self.storyteller_var.get().lower()
        if search_text:
            filtered = [st for st in self.all_storytellers if search_text in st.lower()]
            self.combobox['values'] = filtered
        else:
            self.combobox['values'] = self.all_storytellers

    def _select_storyteller(self) -> None:
        """Select storyteller from combobox."""
        selected = self.combobox.get()
        if selected:
            # Try to find exact match first
            exact_match = None
            for st in self.all_storytellers:
                if normalize_name(st) == normalize_name(selected):
                    exact_match = st
                    break
            
            if exact_match:
                self.combobox.set(exact_match)
                self.storyteller_var.set(exact_match)
                self._on_storyteller_selected()
            else:
                # Try to find partial match
                search_text = normalize_name(selected)
                matches = [st for st in self.all_storytellers if search_text in normalize_name(st)]
                if matches:
                    self.combobox.set(matches[0])
                    self.storyteller_var.set(matches[0])
                    self._on_storyteller_selected()

    def _on_storyteller_selected(self) -> None:
        """Handle storyteller selection and update analytics."""
        storyteller_name = self.storyteller_var.get()
        if not storyteller_name:
            return
        
        # Create analytics for selected storyteller
        self.analytics = StorytellerAnalytics(self.all_games, storyteller_name)
        
        # Update summary
        self._update_summary()
        
        # Rebuild tabs with new data
        self._rebuild_tabs()

    def _update_summary(self) -> None:
        """Update the summary frame with current storyteller stats."""
        if not self.analytics:
            return
        
        games = len(self.analytics.games)
        good_wins = sum(1 for g in self.analytics.games if g.get("winning_team") == "Good")
        evil_wins = games - good_wins
        good_pct = (good_wins / games) * 100 if games > 0 else 0.0
        evil_pct = (evil_wins / games) * 100 if games > 0 else 0.0
        
        self.summary_labels[0].config(text=f"Storyteller: {self.analytics.storyteller_name}")
        self.summary_labels[1].config(text=f"Total Games: {games}")
        self.summary_labels[2].config(text=f"Good Wins: {good_wins} ({good_pct:.1f}%)")
        self.summary_labels[3].config(text=f"Evil Wins: {evil_wins} ({evil_pct:.1f}%)")

    def _rebuild_tabs(self) -> None:
        """Rebuild all tabs with current analytics data."""
        # Clear existing widgets
        for widget in self.frame_scripts.winfo_children():
            widget.destroy()
        for widget in self.frame_characters.winfo_children():
            widget.destroy()
        for widget in self.frame_players.winfo_children():
            widget.destroy()
        
        # Rebuild tabs
        self._build_scripts_tab(self.frame_scripts)
        self._build_characters_tab(self.frame_characters)
        self._build_players_tab(self.frame_players)

    # ---------------------------------------------------------------------
    # Scripts Tab
    # ---------------------------------------------------------------------
    def _build_scripts_tab(self, frame: ttk.Frame) -> None:
        """
        Build the scripts tab.

        Columns are ordered for easier comparison: Good Win %, Evil Win %, Good Wins,
        Evil Wins, Games. Rows are initially sorted by descending Good Win %.

        Clicking a column header will sort the table by that column.
        """
        if not self.analytics:
            tk.Label(frame, text="Please select a storyteller to view script statistics.", font=("Arial", 11)).pack(pady=20)
            return
        
        cols = (
            "Script",
            "Category",
            "Good Win %",
            "Evil Win %",
            "Good Wins",
            "Evil Wins",
            "Games",
        )
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            # Adjust widths for readability
            if col == "Script":
                tree.column(col, anchor="w", width=200)
            elif col == "Category":
                tree.column(col, anchor="center", width=100)
            else:
                tree.column(col, anchor="center", width=100)
        # Function to insert rows into tree
        def populate(sorted_data: List[Any]) -> None:
            tree.delete(*tree.get_children())
            for script, entry in sorted_data:
                games = entry["games"]
                good_wins = entry["good_wins"]
                evil_wins = entry["evil_wins"]
                good_pct = (good_wins / games) * 100 if games > 0 else 0.0
                evil_pct = (evil_wins / games) * 100 if games > 0 else 0.0
                tree.insert(
                    "",
                    "end",
                    values=(
                        script or "(Unknown)",
                        entry["category"],
                        f"{good_pct:.1f}%",
                        f"{evil_pct:.1f}%",
                        good_wins,
                        evil_wins,
                        games,
                    ),
                )
            # Separator row
            tree.insert("", "end", values=("", "", "", "", "", "", ""))
            # Category totals appended
            for cat, tot in self.analytics.category_totals.items():
                games = tot["games"]
                good_wins = tot["good_wins"]
                evil_wins = tot["evil_wins"]
                good_pct = (good_wins / games) * 100 if games > 0 else 0.0
                evil_pct = (evil_wins / games) * 100 if games > 0 else 0.0
                tree.insert(
                    "",
                    "end",
                    values=(
                        f"{cat} Total",
                        cat,
                        f"{good_pct:.1f}%",
                        f"{evil_pct:.1f}%",
                        good_wins,
                        evil_wins,
                        games,
                    ),
                )
        # Prepare initial sorted data (descending by Good Win %)
        items = list(self.analytics.script_stats.items())
        items.sort(key=lambda x: (x[1]["good_wins"] / x[1]["games"] if x[1]["games"] else 0), reverse=True)
        populate(items)
        # Sorting functionality when clicking headers
        def sort_by(col: str) -> None:
            # Determine index in tuple for numeric sorting
            idx_map = {
                "Good Win %": 2,
                "Evil Win %": 3,
                "Good Wins": 4,
                "Evil Wins": 5,
                "Games": 6,
            }
            reverse = getattr(sort_by, "reverse", False)
            if col in idx_map:
                # Build list of tuples (script, entry, computed sort value)
                def compute_value(item):
                    script, entry = item
                    games = entry["games"]
                    good_wins = entry["good_wins"]
                    evil_wins = entry["evil_wins"]
                    if col == "Good Win %":
                        return (good_wins / games) if games else 0
                    if col == "Evil Win %":
                        return (evil_wins / games) if games else 0
                    if col == "Good Wins":
                        return good_wins
                    if col == "Evil Wins":
                        return evil_wins
                    if col == "Games":
                        return games
                    return 0
                sorted_data = sorted(items, key=compute_value, reverse=not reverse)
            else:
                # Sort by script/category names alphabetically
                if col == "Script":
                    sorted_data = sorted(items, key=lambda x: (x[0].lower() if x[0] else ""), reverse=reverse)
                elif col == "Category":
                    sorted_data = sorted(items, key=lambda x: x[1]["category"], reverse=reverse)
                else:
                    sorted_data = items
            setattr(sort_by, "reverse", not reverse)
            populate(sorted_data)
        # Attach sort function to headers
        for col in cols:
            tree.heading(col, text=col, command=lambda c=col: sort_by(c))
        tree.pack(fill="both", expand=True)

    # ---------------------------------------------------------------------
    # Characters Tab
    # ---------------------------------------------------------------------
    def _build_characters_tab(self, frame: ttk.Frame) -> None:
        if not self.analytics:
            tk.Label(frame, text="Please select a storyteller to view character statistics.", font=("Arial", 11)).pack(pady=20)
            return
        
        # Dropdown options: All, each script, category totals
        options: List[str] = ["All"]
        # Unique script names
        options.extend(
            sorted(self.analytics.script_stats.keys(), key=lambda s: s.lower())
        )
        options.append("Normal Total")
        options.append("Teensyville Total")
        sel_var = tk.StringVar(value="All")
        combobox = ttk.Combobox(
            frame, textvariable=sel_var, values=options, state="readonly"
        )
        combobox.pack(padx=5, pady=5, anchor="w")
        # Treeview to display character stats
        # Columns are ordered consistently: Win %, Wins, Games
        cols = ("Character", "Win %", "Wins", "Games")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            if col == "Character":
                tree.column(col, anchor="w", width=200)
            else:
                tree.column(col, anchor="center", width=90)
        tree.pack(fill="both", expand=True)

        def update_character_stats(*args) -> None:
            """Recompute and display character statistics for the selected set of games."""
            # Determine which games to analyse based on selection
            selection = sel_var.get()
            if selection == "All":
                games = self.analytics.games
            elif selection == "Normal Total":
                games = [g for g in self.analytics.games if categorize_script(g.get("game_mode", "")) == "Normal"]
            elif selection == "Teensyville Total":
                games = [g for g in self.analytics.games if categorize_script(g.get("game_mode", "")) == "Teensyville"]
            else:
                games = [g for g in self.analytics.games if (g.get("game_mode", "") or "") == selection]
            # Aggregate statistics per character
            # Use a set to ensure a role is counted only once per game, even if multiple players have the same role (e.g. Legion)
            char_stats: Dict[str, Dict[str, float]] = {}
            for game in games:
                winning_team = game.get("winning_team")
                # Map each role in this game to the list of teams for players with that role
                role_teams: Dict[str, List[str]] = {}
                for p in game.get("players", []):
                    role = p.get("role") or ""
                    if not role:
                        continue
                    role_teams.setdefault(role, []).append(p.get("team"))
                # Update stats per unique role
                for role, teams in role_teams.items():
                    entry = char_stats.setdefault(role, {"games": 0, "wins": 0})
                    entry["games"] += 1
                    # Count a win if any instance of the role was on the winning team
                    if winning_team in teams:
                        entry["wins"] += 1
            # Build data list: (role, win_pct, wins, games)
            data_list = []
            for role, stats in char_stats.items():
                g_count = stats["games"]
                w_count = stats["wins"]
                win_pct = (w_count / g_count) * 100 if g_count > 0 else 0.0
                data_list.append((role, win_pct, w_count, g_count))
            # Sort descending by Win %
            data_list.sort(key=lambda x: x[1], reverse=True)
            # Clear and repopulate the tree
            tree.delete(*tree.get_children())
            for role, pct, wins, games_cnt in data_list:
                tree.insert("", "end", values=(role, f"{pct:.1f}%", wins, games_cnt))

        # Sorting function for column clicks
        def sort_by(col: str) -> None:
            # Column index mapping within displayed values
            idx_map = {"Win %": 1, "Wins": 2, "Games": 3}
            reverse = getattr(sort_by, "reverse", False)
            # Retrieve current rows
            rows = [tree.item(i)["values"] for i in tree.get_children() if tree.item(i)["values"]]
            if col in idx_map:
                idx = idx_map[col]
                def conv(val):
                    if isinstance(val, str) and val.endswith("%"):
                        try:
                            return float(val[:-1])
                        except Exception:
                            return 0.0
                    return float(val)
                rows.sort(key=lambda v: conv(v[idx]), reverse=not reverse)
            else:
                # Sort by character name
                rows.sort(key=lambda v: v[0], reverse=not reverse)
            setattr(sort_by, "reverse", not reverse)
            # Reinsert rows
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)

        for col in cols:
            tree.heading(col, text=col, command=lambda c=col: sort_by(c))
        # Trigger initial population and update on selection change
        combobox.bind("<<ComboboxSelected>>", update_character_stats)
        update_character_stats()

    # ---------------------------------------------------------------------
    # Players Tab
    # ---------------------------------------------------------------------
    def _build_players_tab(self, frame: ttk.Frame) -> None:
        """
        Build the players tab.

        This view uses a drop‑down to select a player and displays a summary of
        their win rates along with a per‑script breakdown. The table columns
        mirror those in the scripts and characters tabs (Win %, Wins, Games and
        corresponding Good/Evil breakdowns) to provide consistency.
        """
        if not self.analytics:
            tk.Label(frame, text="Please select a storyteller to view player statistics.", font=("Arial", 11)).pack(pady=20)
            return
        
        # Player selection combobox
        players = sorted(self.analytics.player_stats.keys())
        sel_var = tk.StringVar()
        combobox = ttk.Combobox(
            frame, textvariable=sel_var, values=players, state="readonly"
        )
        combobox.pack(padx=5, pady=5, anchor="w")
        if players:
            sel_var.set(players[0])
        # Summary frame for overall stats
        summary_frame = tk.LabelFrame(frame, text="Player Summary")
        summary_frame.pack(fill="x", padx=5, pady=5)
        # Labels (stored for easy update)
        lbl_win = tk.Label(summary_frame, text="Win %: 0.0%")
        lbl_win.pack(anchor="w")
        lbl_good = tk.Label(summary_frame, text="Good win %: 0.0%")
        lbl_good.pack(anchor="w")
        lbl_evil = tk.Label(summary_frame, text="Evil win %: 0.0%")
        lbl_evil.pack(anchor="w")
        lbl_games = tk.Label(summary_frame, text="Total games: 0")
        lbl_games.pack(anchor="w")
        lbl_good_games = tk.Label(summary_frame, text="Good games: 0")
        lbl_good_games.pack(anchor="w")
        lbl_evil_games = tk.Label(summary_frame, text="Evil games: 0")
        lbl_evil_games.pack(anchor="w")
        # Treeview columns for per‑script breakdown
        # Counts of wins are omitted – only percentages and game counts are displayed.
        cols = (
            "Script",
            "Win %",
            "Games",
            "Good Win %",
            "Good Games",
            "Evil Win %",
            "Evil Games",
        )
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            if col == "Script":
                tree.column(col, anchor="w", width=180)
            else:
                tree.column(col, anchor="center", width=100)
        tree.pack(fill="both", expand=True)

        def compute_player_summary(player_name: str):
            """Compute aggregated summary and per‑script breakdown for the given player."""
            # Initialize per‑script and overall counters
            per_script: Dict[str, Dict[str, float]] = {}
            overall = {
                "games": 0,
                "wins": 0,
                "good_games": 0,
                "good_wins": 0,
                "evil_games": 0,
                "evil_wins": 0,
            }
            for game in self.analytics.games:
                winning_team = game.get("winning_team")
                script = game.get("game_mode", "") or ""
                for p in game.get("players", []):
                    if p.get("name", "").strip() != player_name:
                        continue
                    team = p.get("team")
                    # Update overall counts
                    overall["games"] += 1
                    if team == winning_team:
                        overall["wins"] += 1
                    if team == "Good":
                        overall["good_games"] += 1
                        if team == winning_team:
                            overall["good_wins"] += 1
                    elif team == "Evil":
                        overall["evil_games"] += 1
                        if team == winning_team:
                            overall["evil_wins"] += 1
                    # Per script
                    s = per_script.setdefault(
                        script,
                        {
                            "games": 0,
                            "wins": 0,
                            "good_games": 0,
                            "good_wins": 0,
                            "evil_games": 0,
                            "evil_wins": 0,
                        },
                    )
                    s["games"] += 1
                    if team == winning_team:
                        s["wins"] += 1
                    if team == "Good":
                        s["good_games"] += 1
                        if team == winning_team:
                            s["good_wins"] += 1
                    elif team == "Evil":
                        s["evil_games"] += 1
                        if team == winning_team:
                            s["evil_wins"] += 1
            return overall, per_script

        def update_player_stats(*args) -> None:
            """Update summary labels and table based on selected player."""
            player_name = sel_var.get()
            if not player_name:
                return
            overall, per_script = compute_player_summary(player_name)
            # Update summary labels
            g = overall["games"]
            w = overall["wins"]
            gg = overall["good_games"]
            gw = overall["good_wins"]
            eg = overall["evil_games"]
            ew = overall["evil_wins"]
            overall_pct = (w / g) * 100 if g > 0 else 0.0
            good_pct = (gw / gg) * 100 if gg > 0 else 0.0
            evil_pct = (ew / eg) * 100 if eg > 0 else 0.0
            lbl_win.config(text=f"Win %: {overall_pct:.1f}%")
            lbl_good.config(text=f"Good win %: {good_pct:.1f}%")
            lbl_evil.config(text=f"Evil win %: {evil_pct:.1f}%")
            lbl_games.config(text=f"Total games: {g}")
            lbl_good_games.config(text=f"Good games: {gg}")
            lbl_evil_games.config(text=f"Evil games: {eg}")
            # Populate tree with per‑script stats
            tree.delete(*tree.get_children())
            # Build list of rows with 'All' then scripts
            rows = []
            # Overall row labelled 'All'
            rows.append(
                (
                    "All",
                    overall_pct,
                    g,
                    good_pct,
                    gg,
                    evil_pct,
                    eg,
                )
            )
            # Individual scripts
            for script, stats in per_script.items():
                g_scr = stats["games"]
                w_scr = stats["wins"]
                gg_scr = stats["good_games"]
                gw_scr = stats["good_wins"]
                eg_scr = stats["evil_games"]
                ew_scr = stats["evil_wins"]
                overall_scr_pct = (w_scr / g_scr) * 100 if g_scr > 0 else 0.0
                good_scr_pct = (gw_scr / gg_scr) * 100 if gg_scr > 0 else 0.0
                evil_scr_pct = (ew_scr / eg_scr) * 100 if eg_scr > 0 else 0.0
                rows.append(
                    (
                        script or "(Unknown)",
                        overall_scr_pct,
                        g_scr,
                        good_scr_pct,
                        gg_scr,
                        evil_scr_pct,
                        eg_scr,
                    )
                )
            # Sort scripts by Win % descending after the first row
            script_rows = rows[1:]
            script_rows.sort(key=lambda x: x[1], reverse=True)
            combined = [rows[0]] + script_rows
            for row in combined:
                # Format percentage columns as strings with one decimal
                tree.insert(
                    "",
                    "end",
                    values=(
                        row[0],
                        f"{row[1]:.1f}%",
                        row[2],
                        f"{row[3]:.1f}%",
                        row[4],
                        f"{row[5]:.1f}%",
                        row[6],
                    ),
                )

        # Sort function for columns
        def sort_by(col: str) -> None:
            # Mapping of column names to index in displayed row values
            idx_map = {
                "Win %": 1,
                "Games": 2,
                "Good Win %": 3,
                "Good Games": 4,
                "Evil Win %": 5,
                "Evil Games": 6,
            }
            reverse = getattr(sort_by, "reverse", False)
            rows = [tree.item(i)["values"] for i in tree.get_children() if tree.item(i)["values"]]
            if col in idx_map:
                idx = idx_map[col]
                def conv(val):
                    if isinstance(val, str) and val.endswith("%"):
                        try:
                            return float(val[:-1])
                        except Exception:
                            return 0.0
                    return float(val)
                rows.sort(key=lambda v: conv(v[idx]), reverse=not reverse)
            else:
                # Sort by script name
                rows.sort(key=lambda v: v[0], reverse=not reverse)
            setattr(sort_by, "reverse", not reverse)
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)

        for col in cols:
            tree.heading(col, text=col, command=lambda c=col: sort_by(c))

        # Bind selection change to update function
        combobox.bind("<<ComboboxSelected>>", update_player_stats)
        # Initial display
        if players:
            update_player_stats()


class PlayerDetailWindow:
    """
    A window showing per‑script and per‑role statistics for a single player.
    """

    def __init__(self, master: tk.Tk, player_name: str, stat: Dict[str, Any]) -> None:
        self.win = tk.Toplevel(master)
        self.win.title(f"{player_name} - Detailed Stats")
        self.win.geometry("600x450")
        # Summary frame
        summ_frame = tk.LabelFrame(self.win, text="Overall Summary")
        summ_frame.pack(fill="x", padx=5, pady=5)
        games = stat["games"]
        wins = stat["wins"]
        good_games = stat["good_games"]
        good_wins = stat["good_wins"]
        evil_games = stat["evil_games"]
        evil_wins = stat["evil_wins"]
        overall_pct = (wins / games) * 100 if games > 0 else 0.0
        good_pct = (good_wins / good_games) * 100 if good_games > 0 else 0.0
        evil_pct = (evil_wins / evil_games) * 100 if evil_games > 0 else 0.0
        tk.Label(summ_frame, text=f"Games: {games}").pack(anchor="w")
        tk.Label(
            summ_frame, text=f"Wins: {wins} ({overall_pct:.1f}%)"
        ).pack(anchor="w")
        tk.Label(
            summ_frame,
            text=f"Good games: {good_games}, Good wins: {good_wins} ({good_pct:.1f}%)",
        ).pack(anchor="w")
        tk.Label(
            summ_frame,
            text=f"Evil games: {evil_games}, Evil wins: {evil_wins} ({evil_pct:.1f}%)",
        ).pack(anchor="w")
        # Notebook for detailed stats
        notebook = ttk.Notebook(self.win)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        # Per‑script statistics tab
        frame_scripts = ttk.Frame(notebook)
        notebook.add(frame_scripts, text="Scripts")
        self._build_script_detail_tab(frame_scripts, stat)
        # Per‑role statistics tab
        frame_roles = ttk.Frame(notebook)
        notebook.add(frame_roles, text="Roles")
        self._build_role_detail_tab(frame_roles, stat)

    def _build_script_detail_tab(self, frame: ttk.Frame, stat: Dict[str, Any]) -> None:
        cols = ("Script", "Games", "Wins", "Win %")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            if col == "Script":
                tree.column(col, anchor="w", width=200)
            else:
                tree.column(col, anchor="center", width=100)
        # Populate per script
        for script, sstat in sorted(stat["scripts"].items(), key=lambda x: x[0].lower()):
            g = sstat["games"]
            w = sstat["wins"]
            pct = (w / g) * 100 if g > 0 else 0.0
            tree.insert(
                "",
                "end",
                values=(script or "(Unknown)", g, w, f"{pct:.1f}%"),
            )
        tree.pack(fill="both", expand=True)

    def _build_role_detail_tab(self, frame: ttk.Frame, stat: Dict[str, Any]) -> None:
        cols = ("Role", "Games", "Wins", "Win %")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            if col == "Role":
                tree.column(col, anchor="w", width=200)
            else:
                tree.column(col, anchor="center", width=100)
        # Compute per‑role statistics (already aggregated in stat["roles"])
        for role, rstat in sorted(stat["roles"].items(), key=lambda x: x[0].lower()):
            g = rstat["games"]
            w = rstat["wins"]
            pct = (w / g) * 100 if g > 0 else 0.0
            tree.insert(
                "",
                "end",
                values=(role, g, w, f"{pct:.1f}%"),
            )
        tree.pack(fill="both", expand=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    gamelog = load_gamelog()
    root = tk.Tk()
    # Attempt to maximize window if supported
    try:
        root.state("zoomed")
    except Exception:
        pass
    AnalyticsUI(root, gamelog)
    root.mainloop()


if __name__ == "__main__":
    main()
