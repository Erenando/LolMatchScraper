import gspread
import json
import re
from google.oauth2.service_account import Credentials

# Google Sheets Auth
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("CGAPIkeys.json", scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)


def get_next_free_row(ws, start_row=5, col_index=1) -> int:
    col_values = ws.col_values(col_index)
    for i in range(start_row, len(col_values) + 2):
        if i > len(col_values) or not col_values[i - 1].strip():
            return i
    return len(col_values) + 2


def _extract_sheet_id(sheets_link: str) -> str:
    m = re.search(r"(?<=docs\.google\.com/spreadsheets/d/)[^/]+", sheets_link)
    if not m:
        raise ValueError("Could not extract Spreadsheet-ID from google_sheets_link.")
    return m.group()

def upload_to_sheets(game_data: list, worksheet_team_name: str) -> None:
    with open("config.json", encoding="utf-8") as json_data:
        data = json.load(json_data)
        sheets_link = data["google_sheets_link"]
        worksheet_name = data["google_sheets_name"] + str(worksheet_team_name)

    sheets_id = _extract_sheet_id(sheets_link)
    sheet = CLIENT.open_by_key(sheets_id)
    ws = sheet.worksheet(worksheet_name)

    values_only_table = [list(row.values()) for row in game_data]

    start_row = get_next_free_row(ws, start_row=5, col_index=1)
    cell_address = f"A{start_row}"

    ws.update(range_name=cell_address, values=values_only_table)
    print("Google Sheets Upload Erfolg!")