import json
import os
import re
import threading

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_cache_lock = threading.Lock()
_client = None
_config_cache = None
_config_mtime = None
_spreadsheet_cache = {}
_worksheet_cache = {}


def _extract_sheet_id(sheets_link: str) -> str:
    match = re.search(r"(?<=docs\.google\.com/spreadsheets/d/)[^/]+", sheets_link)
    if not match:
        raise ValueError("Invalid Google Sheets link in config.json (google_sheets_link).")
    return match.group()


def _load_config() -> dict:
    global _config_cache
    global _config_mtime

    current_mtime = None
    try:
        current_mtime = os.path.getmtime("config.json")
    except OSError:
        pass

    with _cache_lock:
        if _config_cache is not None and _config_mtime == current_mtime:
            return _config_cache

        with open("config.json", encoding="utf-8") as json_data:
            data = json.load(json_data)

        sheets_link = data.get("google_sheets_link", "").strip()
        sheets_name_prefix = data.get("google_sheets_name", "").strip()
        if not sheets_link:
            raise ValueError("config.json: 'google_sheets_link' is missing.")
        if not sheets_name_prefix:
            raise ValueError("config.json: 'google_sheets_name' is missing.")

        _config_cache = data
        _config_mtime = current_mtime
        return _config_cache


def _get_client():
    global _client
    with _cache_lock:
        if _client is None:
            creds = Credentials.from_service_account_file("CGAPIkeys.json", scopes=SCOPES)
            _client = gspread.authorize(creds)
    return _client


def _get_worksheet(sheets_id: str, worksheet_name: str):
    worksheet_cache_key = f"{sheets_id}::{worksheet_name}"
    with _cache_lock:
        if worksheet_cache_key in _worksheet_cache:
            return _worksheet_cache[worksheet_cache_key]

    client = _get_client()
    with _cache_lock:
        if sheets_id not in _spreadsheet_cache:
            _spreadsheet_cache[sheets_id] = client.open_by_key(sheets_id)
        sheet = _spreadsheet_cache[sheets_id]

    worksheet = sheet.worksheet(worksheet_name)
    with _cache_lock:
        _worksheet_cache[worksheet_cache_key] = worksheet
    return worksheet


def upload_to_sheets(game_data: list, worksheet_team_name: str) -> None:
    if not game_data:
        raise ValueError("No game data available for upload.")

    config = _load_config()
    sheets_link = config["google_sheets_link"]
    worksheet_name = f"{config['google_sheets_name']}{worksheet_team_name}"
    sheets_id = _extract_sheet_id(sheets_link)

    ws = _get_worksheet(sheets_id, worksheet_name)
    values_only_table = [list(row.values()) for row in game_data]

    ws.append_rows(
        values_only_table,
        value_input_option="USER_ENTERED",
        insert_data_option="INSERT_ROWS",
        table_range="A5",
    )
