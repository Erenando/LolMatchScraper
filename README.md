# LoL Match Scraper

## Project Overview
A desktop tool for importing League of Legends match stats into Google Sheets. It supports custom/scrim workflows with team-based worksheet targets.

## Description
The app fetches match data from the local League Client (LCU). If LCU is unavailable, it automatically falls back to the Riot Match API. Match rows are parsed, enriched with champion names from Data Dragon, and appended to Google Sheets (no overwrite).

### System Components

| File | Purpose |
|:--- |:--- |
| `UI.py` | Main entry point with the CustomTkinter graphical user interface. |
| `LCUDriver.py` | Connects to the local League Client or falls back to the Riot API. |
| `CustomGameJSONParser.py` | Transforms raw match payloads into upload rows |
| `GoogleAPIConnector.py` | Handles Google authentication and writing rows to the target worksheet. |

---

## Setup

### 1. Google API Preparation
* Follow this [tutorial](https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115) up to minute 6:45 to create a service account.
* Rename the downloaded JSON file to `CGAPIkeys.json` and place it in the project root.

### 2. Configuration (`config.json`)
Configure your file like this:
```json
{
  "google_sheets_link": "YOUR_GOOGLE_SHEET_LINK",
  "google_sheets_name": "Stats_",
  "riot_patch_id": "16.13.1",
  "riot_api_key": "YOUR_RIOT_API_KEY",
  "riot_routing_region": "europe"
}
```
* **google_sheets_name**: Worksheet prefix (the selected team name from `teams.txt` is appended).
* **riot_api_key**: Create a key on [developer.riotgames.com](https://developer.riotgames.com/).
  * **Note:** To get a long-term key, register a personal product under "My Software", otherwise the standard key expires every 24 hours.

### 3. Manage Teams (`teams.txt`)
* Add one team name per line. These names appear in the UI dropdown and determine the target worksheet in Google Sheets.

---

## Usage

1. **Requirement:** If you use LCU mode, start the League of Legends client and log in.
2. **Start:** Run `LoLMatchScraper.exe`.
3. **Input in the UI:**
   * **Own Team:** Taken from the first line in `teams.txt` and shown in the UI.
   * **Game Type:** Choose one of `Scrim`, `Official`, or `Tournament`.
   * **Enemy Team:** Enter the opponent team name.
   * **Match Rows:** Add one or multiple rows, set your side (`Blue`/`Red`) per row, and provide a Match ID per row.
   * **Game ID:** Paste the match ID from match history (for example `7557023906` or `EUW1_7557023906`). The app normalizes both formats.
4. **Finish:** Click **"FETCH & UPLOAD DATA"**. The app shows status feedback and a progress indicator while processing.

### Uploaded Row Fields
Each participant is uploaded as one row with:

`team, player, win, side, champion, kills, deaths, assists, damage_dealt, damage_taken, wards_placed, wards_killed, control_wards, gold, cs, duration, game_type, match_id, match_number`

Notes:
* `player` is stored as `name#hashtag` when a hashtag is available; otherwise only `name`.
* Rows are appended using Google Sheets `append_rows` starting at table range `A5`.

---

### Build Executable (EXE)
If you want to build the EXE yourself, use:
```bash
pyinstaller --noconsole --onefile --name "LolMatchScraper" --add-data "img;img" --icon "img/icon.iso" UI.py
```

### Author
**Eren** | Discord: **Erenando**
