import requests
from LCUDriver import fetch_game_data, get_content

csv_delimiter = ';'

url = "https://ddragon.leagueoflegends.com/cdn/15.7.1/data/en_US/champion.json"
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
    fetch_game_data(game_id)
    content_data = get_content()

    if not content_data:
        raise Exception("Keine Spieldaten gefunden")

    player_names = {
        identity.get('participantId'): identity.get('player', {}).get('gameName', 'UnknownPlayer')
        for identity in content_data.get('participantIdentities', [])
    }

    game_duration_minutes = content_data.get('gameDuration', 0) / 60.0
    data_table = []

    for participant in content_data.get('participants', []):
        participant_id = participant.get('participantId')
        stats = participant.get('stats', {})
        champion_id = participant.get('championId')
        game_name = player_names.get(participant_id, f'UnknownPlayerID_{participant_id}')
        champion = champion_map.get(str(champion_id), str(champion_id))

        data_row = [
            game_name,
            'W' if stats.get('win') else 'L',
            'Blue' if participant.get('teamId') == 100 else 'Red',
            champion,
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