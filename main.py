from GoogleAPIConnector import parse_game, get_sheet_id_for_group

if __name__ == "__main__":
    while True:
        group_name = input("Gruppe (z.B. 3.1): ")
        try:
            get_sheet_id_for_group(group_name).strip()
            break
        except KeyError:
            print(f" Gruppe '{group_name}' ist nicht in der config.json hinterlegt. Bitte erneut versuchen.")
        except ValueError as ve:
            print(f"{ve} Bitte erneut versuchen.")
    game_id = input("Game ID: ")
    worksheet_name = input("Arbeitsblattname (z.B. ScrimStats): ")
    parse_game(game_id, group_name, worksheet_name)