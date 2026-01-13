from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Tuple


@dataclass
class PlayerEntry:
    name: str
    team: str


@dataclass
class GameEntry:
    game_id: int
    winning_team: str
    players: List[PlayerEntry]


def load_games(gamelog_path: Path) -> List[GameEntry]:
    """Load games from JSON file."""
    with gamelog_path.open("r", encoding="utf-8") as f:
        raw_games: List[Dict] = json.load(f)

    games: List[GameEntry] = []
    for g in raw_games:
        players = [
            PlayerEntry(name=p.get("name", ""), team=p.get("team", ""))
            for p in g.get("players", [])
        ]
        games.append(
            GameEntry(
                game_id=g.get("game_id"),
                winning_team=g.get("winning_team"),
                players=players,
            )
        )
    return games


def get_all_player_names(gamelog_path: Path) -> List[str]:
    """Extract all unique player names from the game log."""
    with gamelog_path.open("r", encoding="utf-8") as f:
        raw_games: List[Dict] = json.load(f)
    
    player_names = set()
    for game in raw_games:
        for player in game.get("players", []):
            name = player.get("name", "")
            if name:
                player_names.add(name)
    
    return sorted(list(player_names))


def find_player_team(players: List[PlayerEntry], player_name: str) -> Optional[str]:
    """Find which team a player was on in a game."""
    for p in players:
        if p.name == player_name:
            return p.team
    return None


def analyze_pair(games: List[GameEntry], a: str, b: str) -> Dict[str, object]:
    """Analyze the matchup between two players with Good/Evil breakdowns."""
    together_games: List[Tuple[int, str, str, str]] = []  # (game_id, a_team, b_team, winning_team)
    for game in games:
        a_team = find_player_team(game.players, a)
        b_team = find_player_team(game.players, b)
        if a_team is None or b_team is None:
            continue
        together_games.append((game.game_id, a_team, b_team, game.winning_team))

    same_team_games = [g for g in together_games if g[1] == g[2]]
    opposite_team_games = [g for g in together_games if g[1] != g[2]]

    # Same team breakdown: both Good vs both Evil
    same_team_both_good = [g for g in same_team_games if g[1] == "Good"]
    same_team_both_evil = [g for g in same_team_games if g[1] == "Evil"]
    
    same_team_wins_both_good = sum(1 for (_, a_team, _b_team, w_team) in same_team_both_good if w_team == a_team)
    same_team_wins_both_evil = sum(1 for (_, a_team, _b_team, w_team) in same_team_both_evil if w_team == a_team)

    # Opposite teams breakdown: when a is Good vs when a is Evil
    opp_a_good = [g for g in opposite_team_games if g[1] == "Good"]  # a is Good, b is Evil
    opp_a_evil = [g for g in opposite_team_games if g[1] == "Evil"]  # a is Evil, b is Good
    
    a_wins_when_good = sum(1 for (_gid, a_team, _b_team, w_team) in opp_a_good if w_team == a_team)
    a_wins_when_evil = sum(1 for (_gid, a_team, _b_team, w_team) in opp_a_evil if w_team == a_team)
    
    b_wins_when_good = sum(1 for (_gid, _a_team, b_team, w_team) in opp_a_evil if w_team == b_team)
    b_wins_when_evil = sum(1 for (_gid, _a_team, b_team, w_team) in opp_a_good if w_team == b_team)

    a_wins_opp = a_wins_when_good + a_wins_when_evil
    b_wins_opp = b_wins_when_good + b_wins_when_evil

    def pct(numer: int, denom: int) -> float:
        return (numer / denom * 100.0) if denom else 0.0

    results = {
        "total_together": len(together_games),
        "same_team": {
            "games": len(same_team_games),
            "wins": same_team_wins_both_good + same_team_wins_both_evil,
            "win_pct": round(pct(same_team_wins_both_good + same_team_wins_both_evil, len(same_team_games)), 1),
            "both_good": {
                "games": len(same_team_both_good),
                "wins": same_team_wins_both_good,
                "win_pct": round(pct(same_team_wins_both_good, len(same_team_both_good)), 1),
            },
            "both_evil": {
                "games": len(same_team_both_evil),
                "wins": same_team_wins_both_evil,
                "win_pct": round(pct(same_team_wins_both_evil, len(same_team_both_evil)), 1),
            },
        },
        "opposite_teams": {
            "games": len(opposite_team_games),
            a: {
                "wins": a_wins_opp,
                "win_pct": round(pct(a_wins_opp, len(opposite_team_games)), 1),
                "when_good": {
                    "games": len(opp_a_good),
                    "wins": a_wins_when_good,
                    "win_pct": round(pct(a_wins_when_good, len(opp_a_good)), 1),
                },
                "when_evil": {
                    "games": len(opp_a_evil),
                    "wins": a_wins_when_evil,
                    "win_pct": round(pct(a_wins_when_evil, len(opp_a_evil)), 1),
                },
            },
            b: {
                "wins": b_wins_opp,
                "win_pct": round(pct(b_wins_opp, len(opposite_team_games)), 1),
                "when_good": {
                    "games": len(opp_a_evil),  # b is Good when a is Evil
                    "wins": b_wins_when_good,
                    "win_pct": round(pct(b_wins_when_good, len(opp_a_evil)), 1),
                },
                "when_evil": {
                    "games": len(opp_a_good),  # b is Evil when a is Good
                    "wins": b_wins_when_evil,
                    "win_pct": round(pct(b_wins_when_evil, len(opp_a_good)), 1),
                },
            },
        },
        "game_ids_together": [gid for (gid, _at, _bt, _wt) in together_games],
    }

    return results


class AutocompleteCombobox(ttk.Combobox):
    """A Combobox with autocomplete functionality."""
    
    def __init__(self, parent, values, **kwargs):
        super().__init__(parent, **kwargs)
        self._values = sorted(values)
        self['values'] = self._values
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusIn>', self._on_focus_in)
        self._current_value = ""
    
    def _on_key_release(self, event):
        """Filter values based on typed text."""
        value = self.get().lower()
        
        if event.keysym == 'Return':
            # User pressed Enter, try to match exactly
            current = self.get()
            matches = [v for v in self._values if v.lower() == current.lower()]
            if matches:
                self.set(matches[0])
            return
        
        if len(value) == 0:
            self['values'] = self._values
            return
        
        # Filter values that start with or contain the typed text
        filtered = [v for v in self._values if value in v.lower()]
        self['values'] = filtered
        
        # Auto-complete if there's a single match
        if len(filtered) == 1 and filtered[0].lower().startswith(value):
            current = self.get()
            self.set(filtered[0])
            # Select the text that was added
            self.icursor(len(current))
            self.selection_range(len(current), tk.END)
    
    def _on_focus_in(self, event):
        """Show all values when combobox gets focus."""
        self['values'] = self._values


class StatCard:
    """A visual card widget for displaying statistics."""
    
    def __init__(self, parent, title: str, bg_color: str = "#ffffff"):
        self.frame = tk.Frame(parent, bg=bg_color, relief=tk.RAISED, borderwidth=1)
        self.title_label = tk.Label(
            self.frame,
            text=title,
            font=('Helvetica', 10, 'bold'),
            bg=bg_color,
            fg='#333333',
            wraplength=200,
            justify=tk.CENTER
        )
        self.title_label.pack(pady=(8, 4), fill=tk.X, padx=5)
        
        self.stats_frame = tk.Frame(self.frame, bg=bg_color)
        self.stats_frame.pack(padx=10, pady=(0, 8), fill=tk.BOTH, expand=True)
    
    def add_stat(self, label: str, value: str, row: int, col: int = 0):
        """Add a statistic label-value pair."""
        stat_label = tk.Label(
            self.stats_frame,
            text=label + ":",
            font=('Helvetica', 9),
            bg=self.frame['bg'],
            fg='#666666',
            anchor='w'
        )
        stat_label.grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
        
        value_label = tk.Label(
            self.stats_frame,
            text=value,
            font=('Helvetica', 9, 'bold'),
            bg=self.frame['bg'],
            fg='#000000',
            anchor='w'
        )
        value_label.grid(row=row, column=col+1, sticky=tk.W)
    
    def pack(self, **kwargs):
        """Pack the card frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the card frame."""
        self.frame.grid(**kwargs)


class PlayerComparisonApp:
    """Main application window for player comparison."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Player vs Player Analysis")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f5f5f5')
        
        # Load data
        base_dir = Path(__file__).resolve().parent
        gamelog_path = base_dir / "gamelog.json"
        
        try:
            self.games = load_games(gamelog_path)
            self.player_names = get_all_player_names(gamelog_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load game data: {e}")
            self.games = []
            self.player_names = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Player vs Player Analysis",
            font=('Helvetica', 20, 'bold'),
            bg='#f5f5f5',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Selection frame
        selection_frame = tk.Frame(main_frame, bg='#f5f5f5')
        selection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Player 1 selection
        p1_frame = tk.Frame(selection_frame, bg='#f5f5f5')
        p1_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(p1_frame, text="Player 1:", font=('Helvetica', 11, 'bold'), bg='#f5f5f5').pack(anchor='w')
        self.player1_combo = AutocompleteCombobox(
            p1_frame,
            values=self.player_names,
            width=35,
            font=('Helvetica', 10)
        )
        self.player1_combo.pack(pady=(5, 0))
        
        # Player 2 selection
        p2_frame = tk.Frame(selection_frame, bg='#f5f5f5')
        p2_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(p2_frame, text="Player 2:", font=('Helvetica', 11, 'bold'), bg='#f5f5f5').pack(anchor='w')
        self.player2_combo = AutocompleteCombobox(
            p2_frame,
            values=self.player_names,
            width=35,
            font=('Helvetica', 10)
        )
        self.player2_combo.pack(pady=(5, 0))
        
        # Analyze button
        self.analyze_button = tk.Button(
            selection_frame,
            text="Analyze Matchup",
            command=self._analyze_matchup,
            font=('Helvetica', 11, 'bold'),
            bg='#1976d2',
            fg='white',
            activebackground='#1565c0',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.analyze_button.pack(side=tk.LEFT, padx=20)
        
        # Results container with scrollbar
        results_container = tk.Frame(main_frame, bg='#f5f5f5')
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for results
        self.results_canvas = tk.Canvas(results_container, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=self.results_canvas.yview)
        self.results_frame = tk.Frame(self.results_canvas, bg='#f5f5f5')
        
        def update_scrollregion(event=None):
            self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        
        self.results_frame.bind("<Configure>", update_scrollregion)
        
        canvas_window = self.results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.results_canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.results_canvas.bind('<Configure>', configure_canvas_width)
        self.results_canvas.bind_all("<MouseWheel>", lambda e: self.results_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.results_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial message
        initial_label = tk.Label(
            self.results_frame,
            text="Select two players and click 'Analyze Matchup' to see results.",
            font=('Helvetica', 12),
            bg='#f5f5f5',
            fg='#7f8c8d'
        )
        initial_label.pack(pady=50)
    
    def _analyze_matchup(self):
        """Analyze the matchup between the two selected players."""
        player1 = self.player1_combo.get().strip()
        player2 = self.player2_combo.get().strip()
        
        if not player1 or not player2:
            messagebox.showwarning("Warning", "Please select both players.")
            return
        
        if player1 == player2:
            messagebox.showwarning("Warning", "Please select two different players.")
            return
        
        if player1 not in self.player_names or player2 not in self.player_names:
            messagebox.showerror("Error", "One or both players not found in game data.")
            return
        
        try:
            results = analyze_pair(self.games, player1, player2)
            self._display_results(player1, player2, results)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze matchup: {e}")
    
    def _display_results(self, player1: str, player2: str, results: Dict):
        """Display the analysis results using visual cards."""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Format player names
        p1_display = player1.replace('_', ' ')
        p2_display = player2.replace('_', ' ')
        
        # Header
        header = tk.Label(
            self.results_frame,
            text=f"{p1_display}  vs  {p2_display}",
            font=('Helvetica', 18, 'bold'),
            bg='#f5f5f5',
            fg='#2c3e50'
        )
        header.pack(pady=(0, 10))
        
        total_label = tk.Label(
            self.results_frame,
            text=f"Total Games Together: {results['total_together']}",
            font=('Helvetica', 12),
            bg='#f5f5f5',
            fg='#34495e'
        )
        total_label.pack(pady=(0, 20))
        
        if results['total_together'] == 0:
            no_games_label = tk.Label(
                self.results_frame,
                text="These players have never played together.",
                font=('Helvetica', 11),
                bg='#f5f5f5',
                fg='#7f8c8d'
            )
            no_games_label.pack(pady=20)
            return
        
        # Create main container for cards
        cards_container = tk.Frame(self.results_frame, bg='#f5f5f5')
        cards_container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Same Team Section
        same_team_frame = tk.Frame(cards_container, bg='#f5f5f5')
        same_team_frame.pack(fill=tk.X, pady=(0, 15))
        
        section_title = tk.Label(
            same_team_frame,
            text="SAME TEAM",
            font=('Helvetica', 14, 'bold'),
            bg='#f5f5f5',
            fg='#1976d2'
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        same_team = results['same_team']
        if same_team['games'] > 0:
            # Overall same team stats
            overall_card = StatCard(same_team_frame, "Overall", "#e3f2fd")
            overall_card.pack(fill=tk.X, pady=(0, 10))
            overall_card.add_stat("Games", str(same_team['games']), 0)
            overall_card.add_stat("Wins", str(same_team['wins']), 1)
            overall_card.add_stat("Win Rate", f"{same_team['win_pct']}%", 2)
            
            # Both Good breakdown
            if same_team['both_good']['games'] > 0:
                good_card = StatCard(same_team_frame, "Both Good", "#bbdefb")
                good_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
                good_card.add_stat("Games", str(same_team['both_good']['games']), 0)
                good_card.add_stat("Wins", str(same_team['both_good']['wins']), 1)
                good_card.add_stat("Win Rate", f"{same_team['both_good']['win_pct']}%", 2)
            
            # Both Evil breakdown
            if same_team['both_evil']['games'] > 0:
                evil_card = StatCard(same_team_frame, "Both Evil", "#ffe0b2")
                evil_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
                evil_card.add_stat("Games", str(same_team['both_evil']['games']), 0)
                evil_card.add_stat("Wins", str(same_team['both_evil']['wins']), 1)
                evil_card.add_stat("Win Rate", f"{same_team['both_evil']['win_pct']}%", 2)
        else:
            no_data_label = tk.Label(
                same_team_frame,
                text="No games on the same team",
                font=('Helvetica', 10),
                bg='#f5f5f5',
                fg='#95a5a6'
            )
            no_data_label.pack(anchor='w')
        
        # Opposite Teams Section
        opp_frame = tk.Frame(cards_container, bg='#f5f5f5')
        opp_frame.pack(fill=tk.X, pady=(0, 15))
        
        opp_section_title = tk.Label(
            opp_frame,
            text="OPPOSITE TEAMS",
            font=('Helvetica', 14, 'bold'),
            bg='#f5f5f5',
            fg='#f57c00'
        )
        opp_section_title.pack(anchor='w', pady=(0, 10))
        
        opp = results['opposite_teams']
        if opp['games'] > 0:
            # Overall stats row
            overall_row = tk.Frame(opp_frame, bg='#f5f5f5')
            overall_row.pack(fill=tk.X, pady=(0, 10))
            overall_row.columnconfigure(0, weight=1, uniform='card')
            overall_row.columnconfigure(1, weight=1, uniform='card')
            
            p1_overall = StatCard(overall_row, "Overall", "#e3f2fd")
            p1_overall.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
            p1_overall.add_stat("Games", str(opp['games']), 0)
            p1_overall.add_stat("Wins", str(opp[player1]['wins']), 1)
            p1_overall.add_stat("Win Rate", f"{opp[player1]['win_pct']}%", 2)
            
            p2_overall = StatCard(overall_row, "Overall", "#e3f2fd")
            p2_overall.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
            p2_overall.add_stat("Games", str(opp['games']), 0)
            p2_overall.add_stat("Wins", str(opp[player2]['wins']), 1)
            p2_overall.add_stat("Win Rate", f"{opp[player2]['win_pct']}%", 2)
            
            # Player 1 as Good vs Player 2 as Evil row
            if opp[player1]['when_good']['games'] > 0 or opp[player2]['when_evil']['games'] > 0:
                good_evil_row = tk.Frame(opp_frame, bg='#f5f5f5')
                good_evil_row.pack(fill=tk.X, pady=(0, 10))
                good_evil_row.columnconfigure(0, weight=1, uniform='card')
                good_evil_row.columnconfigure(1, weight=1, uniform='card')
                
                if opp[player1]['when_good']['games'] > 0:
                    p1_good = StatCard(good_evil_row, f"{p1_display} as Good", "#bbdefb")
                    p1_good.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
                    p1_good.add_stat("Games", str(opp[player1]['when_good']['games']), 0)
                    p1_good.add_stat("Wins", str(opp[player1]['when_good']['wins']), 1)
                    p1_good.add_stat("Win Rate", f"{opp[player1]['when_good']['win_pct']}%", 2)
                else:
                    # Empty placeholder to maintain alignment
                    empty_frame = tk.Frame(good_evil_row, bg='#f5f5f5')
                    empty_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
                
                if opp[player2]['when_evil']['games'] > 0:
                    p2_evil = StatCard(good_evil_row, f"{p2_display} as Evil", "#ffe0b2")
                    p2_evil.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
                    p2_evil.add_stat("Games", str(opp[player2]['when_evil']['games']), 0)
                    p2_evil.add_stat("Wins", str(opp[player2]['when_evil']['wins']), 1)
                    p2_evil.add_stat("Win Rate", f"{opp[player2]['when_evil']['win_pct']}%", 2)
                else:
                    # Empty placeholder to maintain alignment
                    empty_frame = tk.Frame(good_evil_row, bg='#f5f5f5')
                    empty_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
            
            # Player 1 as Evil vs Player 2 as Good row
            if opp[player1]['when_evil']['games'] > 0 or opp[player2]['when_good']['games'] > 0:
                evil_good_row = tk.Frame(opp_frame, bg='#f5f5f5')
                evil_good_row.pack(fill=tk.X)
                evil_good_row.columnconfigure(0, weight=1, uniform='card')
                evil_good_row.columnconfigure(1, weight=1, uniform='card')
                
                if opp[player1]['when_evil']['games'] > 0:
                    p1_evil = StatCard(evil_good_row, f"{p1_display} as Evil", "#ffe0b2")
                    p1_evil.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
                    p1_evil.add_stat("Games", str(opp[player1]['when_evil']['games']), 0)
                    p1_evil.add_stat("Wins", str(opp[player1]['when_evil']['wins']), 1)
                    p1_evil.add_stat("Win Rate", f"{opp[player1]['when_evil']['win_pct']}%", 2)
                else:
                    # Empty placeholder to maintain alignment
                    empty_frame = tk.Frame(evil_good_row, bg='#f5f5f5')
                    empty_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
                
                if opp[player2]['when_good']['games'] > 0:
                    p2_good = StatCard(evil_good_row, f"{p2_display} as Good", "#bbdefb")
                    p2_good.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
                    p2_good.add_stat("Games", str(opp[player2]['when_good']['games']), 0)
                    p2_good.add_stat("Wins", str(opp[player2]['when_good']['wins']), 1)
                    p2_good.add_stat("Win Rate", f"{opp[player2]['when_good']['win_pct']}%", 2)
                else:
                    # Empty placeholder to maintain alignment
                    empty_frame = tk.Frame(evil_good_row, bg='#f5f5f5')
                    empty_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        else:
            no_data_label = tk.Label(
                opp_frame,
                text="No games on opposite teams",
                font=('Helvetica', 10),
                bg='#f5f5f5',
                fg='#95a5a6'
            )
            no_data_label.pack(anchor='w')
        
        # Game IDs
        if results['game_ids_together']:
            game_ids_frame = tk.Frame(cards_container, bg='#f5f5f5')
            game_ids_frame.pack(fill=tk.X, pady=(15, 0))
            
            game_ids_label = tk.Label(
                game_ids_frame,
                text=f"Game IDs: {', '.join(map(str, results['game_ids_together']))}",
                font=('Helvetica', 9),
                bg='#f5f5f5',
                fg='#7f8c8d',
                wraplength=900,
                justify=tk.LEFT
            )
            game_ids_label.pack(anchor='w')
        
        # Update scroll region after widgets are created
        self.root.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        self.results_canvas.yview_moveto(0)  # Scroll to top


def main() -> None:
    """Main entry point."""
    root = tk.Tk()
    app = PlayerComparisonApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
