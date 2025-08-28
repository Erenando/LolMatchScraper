import gspread
import os
import json
from google.oauth2.service_account import Credentials
from CustomGameJSONParser import process_game

# Google Sheets Auth
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("CGAPIkeys.json", scopes=scopes)
client = gspread.authorize(creds)

def get_next_free_row(worksheet, start_row=5, col_index=2):
    """Finde die nächste freie Zeile ab start_row in Spalte col_index (1-basiert)."""
    col_values = worksheet.col_values(col_index)
    for i in range(start_row, len(col_values) + 2):
        if i > len(col_values) or not col_values[i - 1].strip():
            return i
    return len(col_values) + 2

def _extract_sheet_id(link: str) -> str:
    if not link:
        raise ValueError("Leerer Link übergeben.")
    if "docs.google.com/spreadsheets/d/" in link:
        return link.split("/d/")[1].split("/")[0]
    raise ValueError("Ungültiger Link übergeben.")

def get_sheet_id_for_group(group_name: str) -> str:
    with open("config.json") as json_data:
        json_result = json.load(json_data)
        sheet_id = json_result.get(group_name)
        if not sheet_id:
            raise ValueError(f"Keine Sheet ID für Gruppe '{group_name}' in config.json gefunden.")
        return _extract_sheet_id(sheet_id)



def parse_game(game_id, group_name, worksheet_name):
    try:

        # Worksheet-Default Name ist "ScrimStats"
        worksheet_name = worksheet_name or "ScrimStats"

        # Falls versehentlich ein kompletter Link übergeben wurde, ID extrahieren
        group_name = get_sheet_id_for_group(group_name)
        
                
        # Sheet & Worksheet öffnen
        sheet = client.open_by_key(group_name)
        worksheet = sheet.worksheet(worksheet_name) if worksheet_name else sheet.get_worksheet(0)

        # Daten aus deinem Parser holen (muss 2D-Liste sein)
        data_table = process_game(game_id)

        # nächste freie Zeile bestimmen und ab Spalte B schreiben
        start_row = get_next_free_row(worksheet)
        cell_address = f"B{start_row}"

        worksheet.update(range_name=cell_address, values=data_table)
        print(f"Tabelle für Game ID {game_id} erfolgreich eingefügt ab {cell_address}.")
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von Game ID {game_id}: {e}")
