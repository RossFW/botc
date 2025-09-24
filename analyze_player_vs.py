from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
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


def find_player_team(players: List[PlayerEntry], player_name: str) -> Optional[str]:
    for p in players:
        if p.name == player_name:
            return p.team
    return None


def analyze_pair(games: List[GameEntry], a: str, b: str) -> Dict[str, object]:
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

    ross_wins_opp = sum(1 for (_gid, a_team, _b_team, w_team) in opposite_team_games if w_team == a_team)
    zoe_wins_opp = len(opposite_team_games) - ross_wins_opp  # exactly one team wins

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
                "wins": ross_wins_opp,
                "win_pct": round(pct(ross_wins_opp, len(opposite_team_games)), 1),
            },
            b: {
                "wins": zoe_wins_opp,
                "win_pct": round(pct(zoe_wins_opp, len(opposite_team_games)), 1),
            },
        },
        "game_ids_together": [gid for (gid, _at, _bt, _wt) in together_games],
    }

    return results


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    gamelog_path = base_dir / "gamelog.json"

    games = load_games(gamelog_path)

    player_a = "Ross_Williams"
    player_b = "Justin_Cobb"

    results = analyze_pair(games, player_a, player_b)

    print("Games with both players:", results["total_together"])
    print("Same team:")
    print(
        f"  games={results['same_team']['games']}  "
        f"wins={results['same_team']['wins']}  "
        f"win%={results['same_team']['win_pct']}%"
    )
    print("Opposite teams:")
    opp = results["opposite_teams"]
    print(
        f"  games={opp['games']}  "
        f"{player_a}: wins={opp[player_a]['wins']} win%={opp[player_a]['win_pct']}%  "
        f"{player_b}: wins={opp[player_b]['wins']} win%={opp[player_b]['win_pct']}%"
    )


if __name__ == "__main__":
    main()


