# NBA Player Comparison CLI

A small command-line tool that compares two NBA players side by side. Type one player's name, then another, and it pulls their stats from the NBA and prints the results as a table right in your terminal.

## Features

- Interactive prompts: enter Player 1, then Player 2
- Flexible name search: full name, partial name, or last name
- Disambiguation menu when a name matches multiple players (active players listed first)
- "Did you mean...?" suggestions for misspelled names
- Two comparison tables: **career** per-game averages and **latest season** per-game averages
- The better value in each row is marked with `*` (for turnovers, lower is better)
- Handles traded players by using their season total across teams
- Compare as many pairs as you like in one session

## Stats Compared

| Stat | Description |
|------|-------------|
| Games Played | Total games |
| Minutes | Minutes per game |
| Points | Points per game |
| Rebounds | Rebounds per game |
| Assists | Assists per game |
| Steals | Steals per game |
| Blocks | Blocks per game |
| Turnovers | Turnovers per game |
| FG% | Field goal percentage |
| 3P% | Three-point percentage |
| FT% | Free throw percentage |

## Requirements

- Python 3.8+
- [`nba_api`](https://github.com/swar/nba_api)
- [`tabulate`](https://pypi.org/project/tabulate/)
- An internet connection (stats are fetched live from stats.nba.com)

## Installation

```bash
git clone https://github.com/AROD2003/nba_player_comparison.git
cd nba_player_comparison
pip install -r requirements.txt
```

## Usage

```bash
python nba_compare.py
```

Example session (stat values below are illustrative):

```
=== NBA Player Comparison ===
Type 'q' at any name prompt to quit.

Player 1: lebron
  -> LeBron James
Player 2: curry
  Multiple matches:
   1. Stephen Curry (active)
   2. Seth Curry (active)
   3. Dell Curry (retired)
  Pick a number (or press Enter to search again): 1
  -> Stephen Curry

CAREER (per game, regular season)
╒══════════════╤════════════════╤═════════════════╕
│ Stat         │  LeBron James  │  Stephen Curry  │
╞══════════════╪════════════════╪═════════════════╡
│ Games Played │     1,500      │      1,000      │
├──────────────┼────────────────┼─────────────────┤
│ Points       │     27.1 *     │      24.5       │
│ ...          │      ...       │       ...       │
╘══════════════╧════════════════╧═════════════════╛

* = better value (for turnovers, lower is better)

Compare another pair? (y/n):
```

### Controls

| Input | Action |
|-------|--------|
| Player name | Search for that player |
| Number (when prompted) | Choose from multiple matches |
| `q`, `quit`, `exit` | Quit at a name prompt |
| `Ctrl+C` | Exit at any time |

## How It Works

1. `nba_api.stats.static.players` finds players by name locally (no network needed for search).
2. `PlayerCareerStats` fetches each player's regular-season totals from stats.nba.com.
3. Totals are converted to per-game averages and shown in a table with `tabulate`.

## Troubleshooting

**Timeouts or connection errors.** stats.nba.com can be slow and sometimes blocks requests, especially from cloud servers or VPNs. The script catches the error and lets you retry. Try again in a moment, or run it from a home network.

**Player not found.** Try the last name only, or check the spelling. The script suggests close matches when it can.

**Newer players show no stats.** Players who haven't played a regular-season game yet have no stats to compare.

## Project Structure

```
.
├── nba_compare.py     # the whole app
├── requirements.txt   # dependencies
├── LICENSE            # MIT
├── .gitignore
└── README.md
```

## Ideas for Future Features

- Playoff stats comparison
- Per-season comparison (pick a specific year)
- Advanced stats (PER, TS%, usage)
- Export results to CSV
- Compare more than two players

## Acknowledgments

This project was built with help from [Claude](https://claude.ai), an AI assistant made by Anthropic.

## Disclaimer

This project is not affiliated with or endorsed by the NBA. Data comes from the public stats endpoints accessed through the `nba_api` package.

## License

Released under the [MIT License](LICENSE).
