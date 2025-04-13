import gspread
from google.oauth2.service_account import Credentials
from CGFormater import get_data_table

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("CGAPIkeys.json", scopes=scopes) #Ganzer pfad halber hurensohn
client = gspread.authorize(creds)

sheets_id = "1oIEf68Axal7UhDMy1fVsD-vCb3zz09TMJBW5wry33E0" #Hier den part der URL nach /d/ einfügen
sheet = client.open_by_key(sheets_id)

worksheet = sheet.worksheet("ScrimStats")  # Name des Arbeitsblatts angeben

# Importiere die Tabelle aus CGFormater
data_table = get_data_table()

# Richtig indexieren in der Google Tabelle
column_b_values = worksheet.col_values(2)  # Spalte B (Index 2)
start_row = 5
for row_index in range(start_row, len(column_b_values) + 2):
    if row_index > len(column_b_values) or (row_index <= len(column_b_values) and not column_b_values[row_index - 1].strip()):
        # Füge die Tabelle ab der ersten leeren Zeile ein
        cell_address = f"B{row_index}"
        worksheet.update(cell_address, data_table)
        print(f"Die Tabelle wurde erfolgreich ab {cell_address} eingefügt.")
        break
worksheet.update_acell("A1",len(column_b_values) + 2) # Teste, ob die Verbindung funktioniert