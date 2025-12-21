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

    for key, team in teams.items():
        print(f"{key} - {team}")

    team_id = input("Geben Sie die Team ID ein: ")
    game_id = input("Geben Sie Ihre Spiel ID ein: ")

    parse_game(teams[int(team_id)], game_id)