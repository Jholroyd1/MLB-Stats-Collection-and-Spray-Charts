# MLB-Stats-Collection-and-Spray-Charts

This project provides a complete workflow for collecting MLB data (play-by-play, box scores, player info) and generating spray charts for any player and date range. It is designed for reproducibility, extensibility, and clarity, with all scripts, schema, and documentation included.

## Features
- **Automated Data Collection:** Scripts to fetch MLB data from the MLB Stats API and store it in a SQLite database.
- **Spray Chart Generation:** Create static (matplotlib) or interactive (Plotly) spray charts for any player and date range.
- **Documented Database Schema:** All relationships and fields are documented in `schema.sql`.
- **Example Data & Outputs:** Sample database, charts, and usage examples included.
- **Reproducible Workflows:** All steps are documented for easy setup and extension.

## Directory Structure
```
MLB_Stats/
├── data/               # SQLite database, CSV exports, sample outputs
├── scripts/            # Data collection and analysis scripts
├── docs/               # Additional documentation
├── .github/            # Project instructions and GitHub workflows
├── requirements.txt    # Python dependencies
├── schema.sql          # Database schema
└── README.md           # Project overview and instructions
```

## Setup
1. **Create a virtual environment:**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```
2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
3. **Initialize the database:**
	```bash
	python scripts/init_database.py
	```

## Data Collection Workflow
The typical workflow for collecting and ensuring complete MLB data is:

1. Use `scripts/collect_mlb_data.py` to fetch game, player, and box score data.
2. Use `scripts/collect_all_play_by_play.py` to fetch play-by-play data for all games.
3. **(Recommended for completeness)** Run the backfill scripts to fill in any missing or incomplete data:
	- `scripts/backfill_missing_boxscores.py` — Fills in missing box score data for games that may have been skipped or failed during initial collection.
	- `scripts/backfill_missing_playbyplay.py` — Fills in missing play-by-play data for games with incomplete or missing event logs.
	- `scripts/backfill_players.py` — Ensures all player information is up to date and fills in any missing player records.

All data is stored in `data/mlb_data.db` (SQLite).

## Database Schema
See `schema.sql` for full details. Main tables:
- **games** - Game results, scores, venue, weather
- **box_scores_batting** - Batting statistics by player/game
- **box_scores_pitching** - Pitching statistics by player/game
- **teams** - Team information
- **players** - Player information
- **play_by_play** - Game events and plays

## Spray Chart Creation
Use `scripts/spray_chart_by_player_and_date.py` to generate a spray chart for any player and date range:
```bash
python scripts/spray_chart_by_player_and_date.py --player "Bryce Harper" --start 2025-04-01 --end 2025-09-30 --output harper_spray_chart.png
```
Output can be PNG (static) or shown interactively.

## Example Usage
- See the `scripts/` directory for more examples (e.g., Ohtani/Harper spray charts).
- Example outputs are in `data/`.

## Data Sources
- MLB Stats API via [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI)

## Contributing
- Fork the repo, create a branch, and submit a pull request.
- Please document any new scripts or workflows in the README and/or `docs/`.

## License
MIT
