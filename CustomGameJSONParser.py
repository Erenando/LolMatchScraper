import requests
import json
from LCUDriver import try_fetch_lcu, get_content

csv_delimiter = ';'

with open("config.json") as json_data:
    json_result = json.load(json_data)
    patch_id = json_result["riot_patch_id"]

url = f"https://ddragon.leagueoflegends.com/cdn/{patch_id}/data/en_US/champion.json"
response = requests.get(url)
data = response.json()
champions = data['data']
champion_map = {champ['key']: champ['id'] for champ in champions.values()}

header = [
    "GameName", "Win/loss", "Side", "Champion", "Kills", "Deaths", "Assists", "DMG Dealt", "DMG Taken",
    "Wards Placed", "Wards Destroyed", "Control Wards", "Gold Earned",
    "CS", "Game Duration"
]

def process_game(game_id):
    raw_data = try_fetch_lcu(game_id)

    if not raw_data:
        raise Exception("Keine Spieldaten gefunden (weder LCU noch Riot API)")

    # Prüfen, ob es Riot API Format (Match-V5) oder LCU Format ist
    is_riot_api = "info" in raw_data

    if is_riot_api:
        info = raw_data["info"]
        participants = info.get("participants", [])
        game_duration_minutes = info.get("gameDuration", 0) / 60.0
    else:
        # LCU Format
        info = raw_data
        participants = raw_data.get("participants", [])
        game_duration_minutes = raw_data.get("gameDuration", 0) / 60.0
        # Player Names Mapping (nur bei LCU nötig)
        player_names_lcu = {
            identity.get('participantId'): identity.get('player', {}).get('gameName', 'Unknown')
            for identity in raw_data.get('participantIdentities', [])
        }

    data_table = []

    for p in participants:
        # Mapping der Felder, da Riot API und LCU teils unterschiedliche Keys nutzen
        if is_riot_api:
            name = p.get('riotIdGameName') or p.get('summonerName')
            win = p.get('win')
            team_id = p.get('teamId')
            # In V5 sind die Stats direkt im Participant Objekt
            stats = p
        else:
            p_id = p.get('participantId')
            name = player_names_lcu.get(p_id, 'Unknown')
            stats = p.get('stats', {})
            win = stats.get('win')
            team_id = p.get('teamId')

        champion_id = p.get('championId')
        champion_name = champion_map.get(str(champion_id), str(champion_id))

        data_row = [
            name,
            'W' if win else 'L',
            'Blue' if team_id == 100 else 'Red',
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

    return data_table