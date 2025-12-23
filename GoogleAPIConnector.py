import gspread
import json
import re
from google.oauth2.service_account import Credentials
from CustomGameJSONParser import process_game

# Google Sheets Auth
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("CGAPIkeys.json", scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)


def get_next_free_row(ws, start_row=5, col_index=2) -> int:
    """
    Sucht die nächste freie Zeile in einer Spalte (Standard: Spalte B).
    """
    col_values = ws.col_values(col_index)
    for i in range(start_row, len(col_values) + 2):
        if i > len(col_values) or not col_values[i - 1].strip():
            return i
    return len(col_values) + 2


def _extract_sheet_id(sheets_link: str) -> str:
    m = re.search(r"(?<=docs\.google\.com/spreadsheets/d/)[^/]+", sheets_link)
    if not m:
        raise ValueError("Konnte Spreadsheet-ID nicht aus google_sheets_link extrahieren.")
    return m.group()


def parse_game(team_name: str, game_id: str) -> None:
    # Kein try-except hier! Lass den Fehler zur UI "hochfliegen"
    with open("config.json", encoding="utf-8") as json_data:
        data = json.load(json_data)
        sheets_link = data["google_sheets_link"]
        worksheet_name = data["google_sheets_name"] + str(team_name)

    sheets_id = _extract_sheet_id(sheets_link)
    sheet = CLIENT.open_by_key(sheets_id)
    ws = sheet.worksheet(worksheet_name)

    # process_game ruft try_fetch_lcu auf
    data_table = process_game(game_id)

    start_row = get_next_free_row(ws, start_row=5, col_index=2)
    cell_address = f"B{start_row}"

    ws.update(range_name=cell_address, values=data_table)
    print(f"Erfolgreich eingefügt in {cell_address}")
