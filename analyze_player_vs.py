from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk, scrolledtext, messagebox
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
    """Analyze the matchup between two players."""
    together_games: List[Tuple[int, str, str, str]] = []  # (game_id, a_team, b_team, winning_team)
    for game in games:
        a_team = find_player_team(game.players, a)
        b_team = find_player_team(game.players, b)
        if a_team is None or b_team is None:
            continue
        together_games.append((game.game_id, a_team, b_team, game.winning_team))

    same_team_games = [g for g in together_games if g[1] == g[2]]
    opposite_team_games = [g for g in together_games if g[1] != g[2]]

    same_team_wins = sum(1 for (_, a_team, _b_team, w_team) in same_team_games if w_team == a_team)

    a_wins_opp = sum(1 for (_gid, a_team, _b_team, w_team) in opposite_team_games if w_team == a_team)
    b_wins_opp = len(opposite_team_games) - a_wins_opp  # exactly one team wins

    def pct(numer: int, denom: int) -> float:
        return (numer / denom * 100.0) if denom else 0.0

    results = {
        "total_together": len(together_games),
        "same_team": {
            "games": len(same_team_games),
            "wins": same_team_wins,
            "win_pct": round(pct(same_team_wins, len(same_team_games)), 1),
        },
        "opposite_teams": {
            "games": len(opposite_team_games),
            a: {
                "wins": a_wins_opp,
                "win_pct": round(pct(a_wins_opp, len(opposite_team_games)), 1),
            },
            b: {
                "wins": b_wins_opp,
                "win_pct": round(pct(b_wins_opp, len(opposite_team_games)), 1),
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


class PlayerComparisonApp:
    """Main application window for player comparison."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Player vs Player Analysis")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
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
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Player vs Player Analysis",
            font=('Helvetica', 18, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Player 1 selection
        ttk.Label(main_frame, text="Player 1:", font=('Helvetica', 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.player1_combo = AutocompleteCombobox(
            main_frame,
            values=self.player_names,
            width=30,
            font=('Helvetica', 10)
        )
        self.player1_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Player 2 selection
        ttk.Label(main_frame, text="Player 2:", font=('Helvetica', 11)).grid(
            row=2, column=0, sticky=tk.W, pady=10
        )
        self.player2_combo = AutocompleteCombobox(
            main_frame,
            values=self.player_names,
            width=30,
            font=('Helvetica', 10)
        )
        self.player2_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Analyze button
        self.analyze_button = ttk.Button(
            main_frame,
            text="Analyze Matchup",
            command=self._analyze_matchup,
            width=20
        )
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Results area
        results_label = ttk.Label(
            main_frame,
            text="Results:",
            font=('Helvetica', 12, 'bold')
        )
        results_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Results text widget with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=('Courier', 10),
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.results_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(5, weight=1)
        
        # Initial message
        self.results_text.insert(tk.END, "Select two players and click 'Analyze Matchup' to see results.\n\n")
        self.results_text.config(state=tk.DISABLED)
    
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
        """Display the analysis results in the text widget."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Format player names (replace underscores with spaces for display)
        p1_display = player1.replace('_', ' ')
        p2_display = player2.replace('_', ' ')
        
        output = []
        output.append("=" * 70)
        output.append(f"  {p1_display}  vs  {p2_display}")
        output.append("=" * 70)
        output.append("")
        
        # Total games together
        output.append(f"Total Games Together: {results['total_together']}")
        output.append("")
        
        if results['total_together'] == 0:
            output.append("These players have never played together.")
        else:
            # Same team statistics
            same_team = results['same_team']
            output.append("─" * 70)
            output.append("SAME TEAM:")
            output.append("─" * 70)
            if same_team['games'] > 0:
                output.append(f"  Games: {same_team['games']}")
                output.append(f"  Wins: {same_team['wins']}")
                output.append(f"  Win Rate: {same_team['win_pct']}%")
            else:
                output.append("  No games on the same team")
            output.append("")
            
            # Opposite teams statistics
            opp = results['opposite_teams']
            output.append("─" * 70)
            output.append("OPPOSITE TEAMS:")
            output.append("─" * 70)
            if opp['games'] > 0:
                output.append(f"  Total Games: {opp['games']}")
                output.append("")
                output.append(f"  {p1_display}:")
                output.append(f"    Wins: {opp[player1]['wins']}")
                output.append(f"    Win Rate: {opp[player1]['win_pct']}%")
                output.append("")
                output.append(f"  {p2_display}:")
                output.append(f"    Wins: {opp[player2]['wins']}")
                output.append(f"    Win Rate: {opp[player2]['win_pct']}%")
            else:
                output.append("  No games on opposite teams")
            output.append("")
            
            # Game IDs
            if results['game_ids_together']:
                game_ids_str = ', '.join(map(str, results['game_ids_together']))
                output.append("─" * 70)
                output.append(f"Game IDs: {game_ids_str}")
        
        output.append("")
        output.append("=" * 70)
        
        self.results_text.insert(tk.END, '\n'.join(output))
        self.results_text.config(state=tk.DISABLED)
        
        # Scroll to top
        self.results_text.see(1.0)


def main() -> None:
    """Main entry point."""
    root = tk.Tk()
    app = PlayerComparisonApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
