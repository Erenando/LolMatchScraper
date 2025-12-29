import multiprocessing
from lcu_driver import Connector
import requests
import json


def _lcu_worker(game_id, return_dict):
    connector = Connector()

    @connector.ready
    async def connect(connection):
        response = await connection.request('GET', f'/lol-match-history/v1/games/{game_id}')
        if response.status == 200:
            return_dict['content'] = await response.json()
        await connector.stop()

    connector.start()


def try_fetch_lcu(game_id: str, timeout_seconds: float = 8.0):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    print(f'Game-ID {game_id} is fetched by LCU...')

    process = multiprocessing.Process(target=_lcu_worker, args=(game_id, return_dict))
    process.start()
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        print("LCU Request to slow (Timeout).")
        process.terminate()
        process.join()

    game_content = return_dict.get('content')

    if game_content:
        print("Data successfully fetched via LCU.")
        create_json(game_content, "LCU")
        return game_content
    else:
        print("LCU not available or no data. Trying Riot API Fallback...")
        riot_data = fetch_from_riot_api(game_id)
        if riot_data is None:
            raise ValueError(f"No Match Data for ID {game_id} found (404).")

        create_json(riot_data, "RIOT")
        return riot_data


def fetch_from_riot_api(game_id: str):
    try:
        with open("config.json") as f:
            config = json.load(f)
            api_key = config.get("riot_api_key")
            routing_region = config.get("riot_routing_region", "europe")

        full_game_id = f"EUW1_{game_id}" if "_" not in str(game_id) else game_id
        url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{full_game_id}"
        headers = {"X-Riot-Token": api_key}

        response = requests.get(url, headers=headers)

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


def create_json(data, origin):
    data_name = origin + "data.json"
    with open(data_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)