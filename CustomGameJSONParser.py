import json
import os
import threading

import requests
from LCUDriver import try_fetch_lcu

_champion_cache_lock = threading.Lock()
_champion_map_cache = {}
_patch_cache = None
_patch_cache_mtime = None
_http_session = requests.Session()


def _load_patch_id() -> str:
    global _patch_cache
    global _patch_cache_mtime

    current_mtime = None
    try:
        current_mtime = os.path.getmtime("config.json")
    except OSError:
        pass

    with _champion_cache_lock:
        if _patch_cache is not None and _patch_cache_mtime == current_mtime:
            return _patch_cache

        with open("config.json", encoding="utf-8") as json_data:
            json_result = json.load(json_data)

        patch_id = json_result.get("riot_patch_id", "").strip()
        if not patch_id:
            raise ValueError("config.json: 'riot_patch_id' is missing.")

        _patch_cache = patch_id
        _patch_cache_mtime = current_mtime
        return _patch_cache


def _get_champion_map(patch_id: str) -> dict:
    with _champion_cache_lock:
        if patch_id in _champion_map_cache:
            return _champion_map_cache[patch_id]

    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_id}/data/en_US/champion.json"
    response = _http_session.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    champions = data.get("data", {})
    champion_map = {champ["key"]: champ["id"] for champ in champions.values()}
    if not champion_map:
        raise ValueError("Champion data could not be loaded.")

    with _champion_cache_lock:
        _champion_map_cache[patch_id] = champion_map
    return champion_map


def process_game(game_id, blue_team_name, red_team_name, game_type, match_number):
    patch_id = _load_patch_id()
    champion_map = _get_champion_map(patch_id)
    raw_data, source_api = try_fetch_lcu(game_id)

    if not raw_data:
        raise Exception("No match data found (neither LCU nor Riot API)")

    is_riot_api = "info" in raw_data

    if is_riot_api:
        info = raw_data["info"]
        participants = info.get("participants", [])
        game_duration_minutes = info.get("gameDuration", 0) / 60.0
        player_names_lcu = {}
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

        data_row = {
            "team": current_team_name,
            "player": name,
            "win": "W" if win else "L",
            "side": str(side),
            "champion": champion_name,
            "kills": stats.get('kills', 0),
            "deaths": stats.get('deaths', 0),
            "assists": stats.get('assists', 0),
            "damage_dealt": stats.get('totalDamageDealtToChampions', 0),
            "damage_taken": stats.get('totalDamageTaken', 0),
            "wards_placed": stats.get('wardsPlaced', 0),
            "wards_killed": stats.get('wardsKilled', 0),
            "control_wards": stats.get('visionWardsBoughtInGame', 0),
            "gold": stats.get('goldEarned', 0),
            "cs": stats.get('totalMinionsKilled', 0) + stats.get('neutralMinionsKilled', 0),
            "duration": round(game_duration_minutes, 2),
            "game_type": game_type,
            "match_id": game_id,
            "match_number": str(match_number),
        }
        data_table.append(data_row)

    return data_table, raw_data, source_api