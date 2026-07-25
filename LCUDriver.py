import multiprocessing
import json
import os
import threading
import time

import requests
from lcu_driver import Connector

_config_lock = threading.Lock()
_config_cache = None
_config_mtime = None
_riot_http_session = requests.Session()
MAX_RIOT_ATTEMPTS = 3


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


def _build_full_game_id(game_id: str) -> str:
    normalized_game_id = str(game_id).strip()
    if "_" in normalized_game_id:
        return normalized_game_id
    return f"EUW1_{normalized_game_id}"


def _retry_wait_seconds(attempt: int) -> float:
    return 0.8 * attempt


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

        full_game_id = _build_full_game_id(game_id)
        url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{full_game_id}"
        headers = {"X-Riot-Token": api_key}

        for attempt in range(1, MAX_RIOT_ATTEMPTS + 1):
            try:
                response = _riot_http_session.get(url, headers=headers, timeout=10)
            except requests.exceptions.Timeout as exc:
                if attempt == MAX_RIOT_ATTEMPTS:
                    raise TimeoutError("Riot API request timed out after multiple retries.") from exc
                time.sleep(_retry_wait_seconds(attempt))
                continue
            except requests.exceptions.RequestException as exc:
                if attempt == MAX_RIOT_ATTEMPTS:
                    raise ConnectionError(f"Riot API request failed: {exc}") from exc
                time.sleep(_retry_wait_seconds(attempt))
                continue

            if response.status_code == 200:
                print("Data successfully fetched via RIOT API.")
                return response.json()

            if response.status_code == 404:
                raise ValueError(f"Game ID {game_id} not found (404).")

            if response.status_code in (401, 403):
                raise PermissionError("Riot API key is invalid or unauthorized (401/403).")

            if response.status_code == 429:
                if attempt == MAX_RIOT_ATTEMPTS:
                    raise RuntimeError("Riot API rate limit reached (429). Please retry shortly.")
                retry_after = response.headers.get("Retry-After")
                wait_seconds = (
                    float(retry_after)
                    if retry_after and retry_after.isdigit()
                    else _retry_wait_seconds(attempt)
                )
                time.sleep(wait_seconds)
                continue

            if 500 <= response.status_code <= 599:
                if attempt == MAX_RIOT_ATTEMPTS:
                    raise RuntimeError(f"Riot API server error ({response.status_code}) after retries.")
                time.sleep(_retry_wait_seconds(attempt))
                continue

            raise RuntimeError(f"Riot API returned error status {response.status_code}.")

        raise RuntimeError("Riot API request failed after retries.")

    except FileNotFoundError:
        raise Exception("config.json not found.")