# LoL Match Scraper

## Project Overview
A tool for automatically importing League of Legends match data into Google Sheets. Ideal for Prime League teams, scrims, and custom games.

## Description
This application fetches match data directly from the League Client (LCU) or through the Riot API fallback. The data is transformed and uploaded to a Google Spreadsheet without overwriting existing rows.

### System Components

| File | Purpose |
|:--- |:--- |
| `UI.py` | Main entry point with the CustomTkinter graphical user interface. |
| `LCUDriver.py` | Connects to the local League Client or falls back to the Riot API. |
| `CustomGameJSONParser.py` | Transforms raw match payloads into row data for Google Sheets. |
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
   * **Team selection:** Defines the destination worksheet in Google Sheets.
   * **Team Blue / Team Red:** Enter both team names.
   * **Game ID:** Paste the match ID from the LoL client history (for example `7557023906` or `EUW1_7557023906`).
4. **Finish:** Click **"FETCH & UPLOAD DATA"**. The app shows status feedback and a progress indicator while processing.

---

### Build Executable (EXE)
If you want to build the EXE yourself, use:
```bash
pyinstaller --noconsole --onefile --name "LolMatchScraper" --add-data "img;img" --icon "img/icon.iso" UI.py
```

### Author
**Eren** | Discord: **Erenando**
