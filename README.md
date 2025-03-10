# daily-silk

Daily AI news fetched from a Discord channel using SILK + discord.py

## Discord Data Fetch and Index

This repository automatically fetches data from a Discord channel, saves it as JSON files, and deploys an index of those files to GitHub Pages. The project runs daily and provides a browsable directory of the collected data.

## Features
- **Daily Data Fetch**: Scrapes the last 10 embedded messages from a specified Discord channel every day at 7:10 AM PST.
- **JSON Storage**: Saves the data in the `data` folder with filenames in the format `YYYYMMDD.json`.
- **GitHub Pages Index**: Automatically generates and deploys a directory listing of the JSON files to GitHub Pages.

## How It Works
1. **Discord Fetch Workflow**: A GitHub Action (`discord-fetch.yml`) runs daily, fetching data using a Python script (`discord_fetch.py`) and committing JSON files to the `data` folder.
2. **Pages Deployment Workflow**: After the fetch completes, another GitHub Action (`deploy-pages.yml`) generates an index of the `data` folder and deploys it to GitHub Pages.

## Setup
- **Discord Token**: The Discord bot token is stored in GitHub Secrets as `DISCORD_TOKEN`.
- **Channel ID**: Hardcoded in `discord_fetch.py` (currently set to `1326603270893867064`).
- **GitHub Pages**: Deployed automatically to `https://<username>.github.io/<repo-name>/`.

## Files
- `discord_fetch.py`: Python script to fetch Discord data.
- `.github/workflows/discord-fetch.yml`: Workflow for daily data fetching.
- `.github/workflows/deploy-pages.yml`: Workflow for deploying the index to GitHub Pages.
- `data/`: Folder containing the generated JSON files (e.g., `20250310.json`).

## Credits
- Inspired by the innovative work of [KingBootoshi](https://x.com/KingBootoshi), creator of SILK.
- Built with assistance from Grok 3 by xAI.

## Usage
- View the latest data at the GitHub Pages URL.
- Trigger workflows manually via the GitHub Actions tab if needed.
