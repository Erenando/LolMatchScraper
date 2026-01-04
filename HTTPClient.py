import json
import requests

with open("config.json") as json_data:
    json_result = json.load(json_data)
    url = json_result["dome_api_url"]
    api_key = json_result["dome_api_key"]

headers = {
    'accept': 'application/json',
    'Key': api_key,
}

def send_to_api(game_data: list, game_id: str, game_type: str, game_nr: str, team1_name: str, team2_name: str) -> None:
    winning_team = "Unknown"
    for row in game_data:
        if row.get("win") == "W":
            winning_team = row.get("team")
            break

    payload_dict = {
        "matchId": str(game_id),
        "GameType": game_type,
        "0": team1_name,
        "1": team2_name,
        "win": 0 if winning_team == team1_name else 1,
        "GameNr": int(game_nr),
        "data": game_data
    }

    print(f"Send Payload for Game {game_id} (Type: {game_type}, Nr: {game_nr}, Winner: {winning_team})")

    try:
        response = requests.post(url, headers=headers, json=payload_dict)
        response.raise_for_status()

        print("HTTP API Erfolg! Status Code:", response.status_code)

    except requests.exceptions.RequestException as e:
        print(f"HTTP API Fehler: {e}")
        if e.response is not None:
            print("Server Antwort:", e.response.text)
        raise Exception(f"HTTP Upload Failed: {e}")