from lcu_driver import Connector
import threading
import time
import requests
import json

connector = Connector()

game_content = None
game_id_to_fetch = None

_done_event = threading.Event()
_started_event = threading.Event()


async def get_data(connection, game_id):
    global game_content
    response = await connection.request('GET', f'/lol-match-history/v1/games/{game_id}')
    if response.status == 200:
        game_content = await response.json()
        print('Daten erfolgreich abgerufen')
    else:
        print(f'Fehler: {response.status}')

@connector.ready
async def connect(connection):
    global game_id_to_fetch
    _started_event.set()
    print('LCU API is ready to be used.')

    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Bitte im Client einloggen und Script neu starten...')
        _done_event.set()
        await connector.stop()
        return

    if game_id_to_fetch:
        print(f'Game-ID {game_id_to_fetch} wird abgerufen ...')
        await get_data(connection, game_id_to_fetch)

    _done_event.set()
    await connector.stop()

@connector.close
async def disconnect(_):
    print('Verbindung zum League Client getrennt.')
    _done_event.set()

def get_content():
    return game_content

def try_fetch_lcu(game_id: str, timeout_seconds: float = 5.0):
    global game_content, game_id_to_fetch

    game_content = None
    game_id_to_fetch = game_id
    _done_event.clear()
    _started_event.clear()

    def _runner():
        try:
            connector.start()
        except Exception as e:
            print(f"LCU konnte nicht gestartet werden: {e}")
            _done_event.set()

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _done_event.is_set():
            break
        time.sleep(0.05)

    if not _done_event.is_set():
        print("LCU Timeout - Fallback mit Riot API")
        game_content = fetch_from_riot_api(game_id)
        return game_content

    return game_content


def fetch_from_riot_api(game_id: str):
    with open("config.json") as f:
        config = json.load(f)
        api_key = config.get("riot_api_key")
        routing_region = config.get("riot_routing_region", "europe")

    full_game_id = f"EUW1_{game_id}" if "_" not in str(game_id) else game_id

    url = f"https://{routing_region}.api.riotgames.com/lol/match/v5/matches/{full_game_id}"
    headers = {"X-Riot-Token": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Daten erfolgreich über Riot API abgerufen.")
        return response.json()
    else:
        print(f"Riot API Fehler: {response.status_code} - {response.text}")
        return None


