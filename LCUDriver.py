import multiprocessing
import json
import os
import threading

import requests
from lcu_driver import Connector

_config_lock = threading.Lock()
_config_cache = None
_config_mtime = None
_riot_http_session = requests.Session()


def _lcu_worker(game_id, result_dict):
    connector = Connector()

    @connector.ready
    async def connect(connection):
        response = await connection.request('GET', f'/lol-match-history/v1/games/{game_id}')
        if response.status == 200:
            result_dict["content"] = await response.json()
        await connector.stop()

    try:
        connector.start()
    except Exception:
        result_dict["content"] = None


def _load_config() -> dict:
    global _config_cache
    global _config_mtime

    current_mtime = None
    try:
        current_mtime = os.path.getmtime("config.json")
    except OSError:
        pass

    with _config_lock:
        if _config_cache is not None and _config_mtime == current_mtime:
            return _config_cache

        with open("config.json", encoding="utf-8") as config_file:
            config = json.load(config_file)

        _config_cache = config
        _config_mtime = current_mtime
        return _config_cache


def try_fetch_lcu(game_id: str, timeout_seconds: float = 8.0):
    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    print(f'Game-ID {game_id} is fetched by LCU...')

    process = multiprocessing.Process(target=_lcu_worker, args=(game_id, result_dict))
    process.start()
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        print("LCU Request too slow (Timeout).")
        process.terminate()
        process.join()

    game_content = result_dict.get("content")

    if game_content:
        print("Data successfully fetched via LCU.")
        return game_content, "lcu"
    else:
        print("LCU not available or no data. Trying Riot API Fallback...")
        riot_data = fetch_from_riot_api(game_id)
        if riot_data is None:
            raise ValueError(f"No Match Data for ID {game_id} found (404).")

        return riot_data, "riot"

def fetch_from_riot_api(game_id: str):
    try:
        config = _load_config()
        api_key = config.get("riot_api_key", "").strip()
        routing_region = config.get("riot_routing_region", "europe").strip()
        if not api_key:
            raise ValueError("config.json: 'riot_api_key' is missing.")

        full_game_id = f"EUW1_{game_id}" if "_" not in str(game_id) else game_id
        url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{full_game_id}"
        headers = {"X-Riot-Token": api_key}

        response = _riot_http_session.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("Data successfully fetched via RIOT API.")
            return response.json()
        elif response.status_code == 404:
            raise ValueError(f"Game ID {game_id} not found (404).")
        else:
            raise Exception(f"Riot API Error: {response.status_code}")

    except FileNotFoundError:
        raise Exception("config.json not found.")
    except Exception as e:
        raise e