# daily-silk

Daily AI news fetched from a Discord channel using SILK + discord.py

## Discord Data Fetch and Index

This repository automatically fetches embedded messages from a Discord channel, saves them as both JSON and Markdown files per day, and deploys an index to GitHub Pages. The project provides flexible data collection and a browsable archive of AI news.

## Features
- **Multi-Day Fetch**: Collects embedded messages for a specified number of days, ending at a target date (default: today).
- **Dual Format Storage**: Saves data as JSON (`YYYY-MM-DD.json`) and Markdown (`YYYY-MM-DD.md`) files in the `data` folder, with messages ordered from start to end of each day.
- **Deduplication**: Ensures no duplicate messages within each day's data.
- **GitHub Pages Index**: Deploys a directory listing of the data files to GitHub Pages.
- **Command-Line Control**: Supports options for date range, clearing existing data, and more.

## How It Works
1. **Discord Fetch**: The Python script (`discord_fetch.py`) fetches embedded messages from a Discord channel, organizes them by date, and saves them in JSON and Markdown formats.
2. **Workflow Automation**:
   - `discord-fetch.yml`: Runs daily at 7:10 AM PST, fetching and committing data files.
   - `deploy-pages.yml`: Generates and deploys an index of the `data` folder to GitHub Pages after each fetch.
3. **Output**: Each day's data is stored in `data/YYYY-MM-DD.json` (structured data) and `data/YYYY-MM-DD.md` (human-readable format).

## Setup
- **Discord Token**: Stored in GitHub Secrets as `DISCORD_TOKEN`.
- **Channel ID**: Hardcoded in `discord_fetch.py` (currently `1326603270893867064`).
- **GitHub Pages**: Deployed to `https://<username>.github.io/daily-silk/`.
- **Dependencies**: Requires `discord.py` (install via `pip install discord.py`).

## Usage
Run the script locally with command-line options:
- `python discord_fetch.py` - Fetches today's messages into `YYYY-MM-DD.json` and `.md`.
- `python discord_fetch.py --date YYYY-MM-DD` - Fetches messages for a specific end date.
- `python discord_fetch.py --days N` - Fetches N days ending at the target date (default: 1).
- `python discord_fetch.py --clear` - Clears existing files before fetching new data.
- Example: `python discord_fetch.py --date 2025-03-13 --days 3` - Fetches March 11-13, 2025.

View the archive at the GitHub Pages URL or trigger workflows manually via the GitHub Actions tab.

## Files
- `discord_fetch.py`: Main script for fetching and processing Discord data.
- `.github/workflows/discord-fetch.yml`: Daily fetch workflow.
- `.github/workflows/deploy-pages.yml`: Pages deployment workflow.
- `data/`: Contains generated JSON and Markdown files (e.g., `2025-03-13.json`, `2025-03-13.md`).

## Output Format
- **JSON**: Array of objects with `timestamp` and `description` fields.
- **Markdown**: Daily summary with a top-level header (`# Daily Summary for YYYY-MM-DD`) and entries sorted chronologically (earliest to latest), each with a timestamp header (`## YYYY-MM-DD HH:MM:SS`) and description.

## Credits
- Inspired by [KingBootoshi](https://x.com/KingBootoshi), creator of SILK.
- Built with assistance from Grok 3 by xAI.

## Notes
- Messages are fetched without a hard limit (previously 10 embeds), capturing all embeds in the date range.
- Markdown files enhance readability, complementing the structured JSON output.
