from GoogleAPIConnector import parse_game

if __name__ == "__main__":
    teams = {}
    with open("teams.txt", encoding="utf-8") as file:
        i = 1
        for line in file:
            name = line.strip().upper()
            if name:
                teams.update({i: name})
                i += 1

    while True:
        for key, team in teams.items():
            print(f"{key} - {team}")

        try:
            team_input = input("Geben Sie die Team ID ein: ")

            team_id = int(team_input)
            if team_id not in teams:
                print("Ungültige Team ID!")
                continue

            game_id = input("Geben Sie Ihre Spiel ID ein: ").strip()
            if not game_id:
                print("Keine Game ID eingegeben!")
                continue

            parse_game(teams[team_id], game_id)
            print("\n--- Verarbeitung abgeschlossen. Nächste Eingabe: ---\n")

        except ValueError:
            print("Bitte geben Sie eine gültige Zahl für die Team ID ein.")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")