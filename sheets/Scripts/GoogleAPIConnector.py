import gspread
from google.oauth2.service_account import Credentials
from JSONParser import process_game

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("CGAPIkeys.json", scopes=scopes)
client = gspread.authorize(creds)

sheets_id = "1oIEf68Axal7UhDMy1fVsD-vCb3zz09TMJBW5wry33E0"
sheet = client.open_by_key(sheets_id)
worksheet = sheet.worksheet("ScrimStats")

def get_next_free_row(start_row=5, col_index=2):
    col_values = worksheet.col_values(col_index)
    for i in range(start_row, len(col_values) + 2):
        if i > len(col_values) or not col_values[i - 1].strip():
            return i
    return len(col_values) + 2

def parse_game():
    game_id = input("Welche gameId möchtest du abrufen? ")
    try:
        data_table = process_game(game_id)
        if not data_table:
            print(f"Keine Daten für Game ID {game_id} gefunden.")

        start_row = get_next_free_row()
        cell_address = f"B{start_row}"
        worksheet.update(range_name=cell_address, values=data_table)
        print(f"Tabelle für Game ID {game_id} erfolgreich eingefügt ab {cell_address}.")
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von Game ID {game_id}: {e}")
