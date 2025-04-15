import asyncio
from lcu_driver import Connector

connector = Connector()
game_content = None
game_id_to_fetch = None  # wird extern gesetzt

async def get_data(connection, gameID):
    global game_content
    response = await connection.request('GET', f'/lol-match-history/v1/games/{gameID}')
    if response.status == 200:
        game_content = await response.json()
        print('Daten erfolgreich abgerufen')
    else:
        print(f'Fehler: {response.status}')

@connector.ready
async def connect(connection):
    global game_id_to_fetch
    print('LCU API is ready to be used.')

    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Bitte im Client einloggen und Script neu starten...')
        return

    if game_id_to_fetch:
        print(f'Game-ID {game_id_to_fetch} wird abgerufen ...')
        await get_data(connection, game_id_to_fetch)
        await connector.stop()  # optional: beende Verbindung danach

@connector.close
async def disconnect(_):
    print('Verbindung zum League Client getrennt.')

def get_content():
    return game_content

def fetch_game_data(game_id):
    global game_id_to_fetch
    game_id_to_fetch = game_id
    connector.start()  # startet asynchron den ganzen Ablauf
