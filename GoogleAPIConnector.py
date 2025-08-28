import gspread
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

def parse_game(game_id, sheet_id, worksheet_name):
    """
    Parst ein Game und schreibt die Daten in das Google Sheet.
    - sheet_id: die Google Sheet ID (oder vollständiger Link; ID wird automatisch extrahiert)
    - worksheet_name (optional): Name des Tabellenblatts; wenn None => 1. Blatt
    """
    try:
        # Falls versehentlich ein kompletter Link übergeben wurde, ID extrahieren
        if "docs.google.com/spreadsheets/d/" in sheet_id:
            # Robust ohne re: splitten und den Teil nach /d/ nehmen
            sheet_id = sheet_id.split("/d/")[1].split("/")[0]
        if not worksheet_name:
            worksheet_name = "ScrimStats"
                
        # Sheet & Worksheet öffnen
        sheet = client.open_by_key(sheet_id)
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
