import multiprocessing
from lcu_driver import Connector
import requests
import json


# Diese Funktion läuft in einem komplett isolierten Prozess
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
    # Manager für den Datenaustausch zwischen Prozessen
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    print(f'Game-ID {game_id} wird über LCU abgerufen...')

    # Prozess erstellen
    process = multiprocessing.Process(target=_lcu_worker, args=(game_id, return_dict))
    process.start()

    # Auf den Prozess warten (Timeout)
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        print("LCU Abfrage zu langsam (Timeout).")
        process.terminate()
        process.join()

    game_content = return_dict.get('content')

    if game_content:
        print("Daten erfolgreich über LCU abgerufen.")
        return game_content
    else:
        print("LCU nicht verfügbar oder keine Daten. Versuche Riot API Fallback...")
        riot_data = fetch_from_riot_api(game_id)
        if riot_data is None:
            raise ValueError(f"Keine Spieldaten für ID {game_id} gefunden (404).")

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
            print("Daten erfolgreich über Riot API abgerufen.")
            return response.json()
        elif response.status_code == 404:
            # Dieser Text wird direkt in der UI angezeigt
            raise ValueError(f"Game ID {game_id} wurde nicht gefunden (404).")
        else:
            raise Exception(f"Riot API Fehler: {response.status_code}")

    except FileNotFoundError:
        raise Exception("config.json wurde nicht gefunden.")
    except Exception as e:
        # Reiche den Fehler weiter, anstatt ihn nur zu printen
        raise e