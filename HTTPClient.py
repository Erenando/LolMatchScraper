import json
import requests
from CustomGameJSONParser import process_game

with open("config.json") as json_data:
    json_result = json.load(json_data)
    url = json_result["dome_api_url"]
    api_key = json_result["dome_api_key"]


headers = {
    'accept': 'application/json',
    'Key': api_key,
}

def parse_game(blue_team: str, red_team: str, game_id: str) -> None:
    data_rows = process_game(game_id, blue_team, red_team)
    payload_dict = {
        "matchId": str(game_id),
        "data": data_rows
    }

    print(payload_dict)

    try:
        response = requests.post(url, headers=headers, json=payload_dict)
        response.raise_for_status()

        print("Erfolg! Status Code:", response.status_code)
        print("Antwort:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        if e.response is not None:
            print("Server Antwort:", e.response.text)
