from GoogleAPIConnector import parse_game

if __name__ == "__main__":
    sheet_id = input("Geben Sie Ihre Google Sheet Link oder ID ein: ")
    game_id = input("Geben Sie Ihre Spiel ID ein: ")
    worksheet_name = input("Geben Sie den Namen des Arbeitsblatts ein oder drücken Sie Enter für den default value (ScrimStats): ")
    parse_game(game_id, sheet_id, worksheet_name)