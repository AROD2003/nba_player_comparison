#!/usr/bin/env python3
"""
NBA Player Comparison (command line)

Type one player, then another. The script looks both up and prints a
side-by-side table of career and latest-season per-game stats.

Setup:
    pip install nba_api tabulate

Run:
    python nba_compare.py
"""

import difflib
import sys

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from tabulate import tabulate

TIMEOUT = 30  # seconds to wait on stats.nba.com

# (label, key, lower_is_better)
STAT_ROWS = [
    ("Games Played", "GP", False),
    ("Minutes", "MPG", False),
    ("Points", "PPG", False),
    ("Rebounds", "RPG", False),
    ("Assists", "APG", False),
    ("Steals", "SPG", False),
    ("Blocks", "BPG", False),
    ("Turnovers", "TOV", True),
    ("FG%", "FG_PCT", False),
    ("3P%", "FG3_PCT", False),
    ("FT%", "FT_PCT", False),
]


# ---------------------------------------------------------------- lookup
def find_player(prompt):
    """Ask for a name until we get one valid player dict."""
    while True:
        query = input(prompt).strip()
        if not query:
            continue
        if query.lower() in ("q", "quit", "exit"):
            sys.exit(0)

        # Try full-name match, then last-name match
        matches = players.find_players_by_full_name(query)
        if not matches:
            matches = players.find_players_by_last_name(query)

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            # Prefer active players first, then alphabetical
            matches.sort(key=lambda p: (not p["is_active"], p["full_name"]))
            matches = matches[:10]
            print("  Multiple matches:")
            for i, p in enumerate(matches, 1):
                tag = "active" if p["is_active"] else "retired"
                print(f"   {i}. {p['full_name']} ({tag})")
            choice = input("  Pick a number (or press Enter to search again): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                return matches[int(choice) - 1]
            continue

        # No matches: suggest close names
        names = [p["full_name"] for p in players.get_players()]
        close = difflib.get_close_matches(query, names, n=3, cutoff=0.6)
        print(f"  No player found for '{query}'.")
        if close:
            print("  Did you mean: " + ", ".join(close) + "?")


# ----------------------------------------------------------------- stats
def per_game(row):
    """Turn a totals row into per-game numbers."""
    gp = float(row["GP"]) or 1.0
    return {
        "GP": int(row["GP"]),
        "MPG": float(row["MIN"]) / gp,
        "PPG": float(row["PTS"]) / gp,
        "RPG": float(row["REB"]) / gp,
        "APG": float(row["AST"]) / gp,
        "SPG": float(row["STL"]) / gp,
        "BPG": float(row["BLK"]) / gp,
        "TOV": float(row["TOV"]) / gp,
        "FG_PCT": float(row["FG_PCT"] or 0) * 100,
        "FG3_PCT": float(row["FG3_PCT"] or 0) * 100,
        "FT_PCT": float(row["FT_PCT"] or 0) * 100,
    }


def fetch_stats(player):
    """Return (career_stats, latest_season_stats, latest_season_label)."""
    career = playercareerstats.PlayerCareerStats(
        player_id=player["id"], timeout=TIMEOUT
    )
    seasons_df = career.season_totals_regular_season.get_data_frame()
    career_df = career.career_totals_regular_season.get_data_frame()

    if seasons_df.empty or career_df.empty:
        return None, None, None

    # A traded player has per-team rows plus a "TOT" row for the season.
    # Use the last row, which is the season total when "TOT" exists.
    last_season = seasons_df["SEASON_ID"].iloc[-1]
    season_rows = seasons_df[seasons_df["SEASON_ID"] == last_season]
    tot = season_rows[season_rows["TEAM_ABBREVIATION"] == "TOT"]
    latest_row = (tot if not tot.empty else season_rows).iloc[-1]

    return per_game(career_df.iloc[0]), per_game(latest_row), last_season


# ---------------------------------------------------------------- output
def fmt(key, value):
    if key == "GP":
        return f"{value:,}"
    if key.endswith("PCT"):
        return f"{value:.1f}"
    return f"{value:.1f}"


def build_rows(name_a, stats_a, name_b, stats_b):
    """Build table rows, marking the better value with a star."""
    rows = []
    for label, key, lower_better in STAT_ROWS:
        a, b = stats_a[key], stats_b[key]
        a_txt, b_txt = fmt(key, a), fmt(key, b)

        if round(a, 3) != round(b, 3):
            a_wins = a < b if lower_better else a > b
            if a_wins:
                a_txt += " *"
            else:
                b_txt += " *"
        rows.append([label, a_txt, b_txt])
    return rows


def print_table(title, name_a, stats_a, name_b, stats_b):
    print(f"\n{title}")
    rows = build_rows(name_a, stats_a, name_b, stats_b)
    print(tabulate(rows, headers=["Stat", name_a, name_b], tablefmt="fancy_grid",
                   colalign=("left", "center", "center")))


def compare(p1, p2):
    print("\nFetching stats from stats.nba.com...")
    try:
        c1, s1, season1 = fetch_stats(p1)
        c2, s2, season2 = fetch_stats(p2)
    except Exception as exc:  # network errors, timeouts, rate limits
        print(f"\nCouldn't fetch stats: {exc}")
        print("stats.nba.com can be slow or block requests. Try again in a moment.")
        return

    for p, c in ((p1, c1), (p2, c2)):
        if c is None:
            print(f"\nNo regular-season stats found for {p['full_name']}.")
            return

    n1, n2 = p1["full_name"], p2["full_name"]
    print_table("CAREER (per game, regular season)", n1, c1, n2, c2)
    print_table(f"LATEST SEASON ({n1}: {season1}, {n2}: {season2})", n1, s1, n2, s2)
    print("\n* = better value (for turnovers, lower is better)")


# ------------------------------------------------------------------ main
def main():
    print("=== NBA Player Comparison ===")
    print("Type 'q' at any name prompt to quit.\n")

    while True:
        p1 = find_player("Player 1: ")
        print(f"  -> {p1['full_name']}")
        p2 = find_player("Player 2: ")
        print(f"  -> {p2['full_name']}")

        compare(p1, p2)

        again = input("\nCompare another pair? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            break
        print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
