import requests
import json
from LCUDriver import try_fetch_lcu

with open("config.json") as json_data:
    json_result = json.load(json_data)
    patch_id = json_result["riot_patch_id"]

url = f"https://ddragon.leagueoflegends.com/cdn/{patch_id}/data/en_US/champion.json"
response = requests.get(url)
data = response.json()
champions = data['data']
champion_map = {champ['key']: champ['id'] for champ in champions.values()}

def process_game(game_id, blue_team_name, red_team_name):
    global player_names_lcu
    raw_data = try_fetch_lcu(game_id)

    if not raw_data:
        raise Exception("No match data found (neither LCU nor Riot API)")

    is_riot_api = "info" in raw_data

    if is_riot_api:
        info = raw_data["info"]
        participants = info.get("participants", [])
        game_duration_minutes = info.get("gameDuration", 0) / 60.0
    else:
        participants = raw_data.get("participants", [])
        game_duration_minutes = raw_data.get("gameDuration", 0) / 60.0
        player_names_lcu = {
            identity.get('participantId'): identity.get('player', {}).get('gameName', 'Unknown')
            for identity in raw_data.get('participantIdentities', [])
        }

    data_table = []

    for p in participants:
        if is_riot_api:
            name = p.get('riotIdGameName') or p.get('summonerName')
            win = p.get('win')
            stats = p
        else:
            p_id = p.get('participantId')
            name = player_names_lcu.get(p_id, 'Unknown')
            stats = p.get('stats', {})
            win = stats.get('win')


        champion_id = p.get('championId')
        champion_name = champion_map.get(str(champion_id), str(champion_id))
        team_id = p.get('teamId')
        side = 'Blue' if team_id == 100 else 'Red'
        current_team_name = blue_team_name if side == 'Blue' else red_team_name

        data_row = [
            current_team_name,
            name,
            'W' if win else 'L',
            side,
            champion_name,
            stats.get('kills', 0),
            stats.get('deaths', 0),
            stats.get('assists', 0),
            stats.get('totalDamageDealtToChampions', 0),
            stats.get('totalDamageTaken', 0),
            stats.get('wardsPlaced', 0),
            stats.get('wardsKilled', 0),
            stats.get('visionWardsBoughtInGame', 0),
            stats.get('goldEarned', 0),
            stats.get('totalMinionsKilled', 0) + stats.get('neutralMinionsKilled', 0),
            round(game_duration_minutes, 2)
        ]
        data_table.append(data_row)

    create_json(data_table)
    return data_table


def create_json(google_sheets_data):
    with open("google_sheets_data.json", "w", encoding="utf-8") as json_file:
        json.dump(google_sheets_data, json_file, indent=4)