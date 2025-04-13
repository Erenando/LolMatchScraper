from lcu_driver import Connector

connector = Connector()
game_content = None  # globale Variable

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
    print('LCU API is ready to be used.')
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Bitte im Client einloggen und Script neu starten...')
    else:
        print('fetching League Client data ...')
        game_id = input("Bitte geben Sie eine gameId ein: ")
        await get_data(connection, game_id)

@connector.close
async def disconnect(_):
    print('disconnected')

def start_connector():
    connector.start()

def get_content():
    return game_content  # Zugriff auf globale Variable

# Start
start_connector()
# Beispiel: irgendwo anders im Code (funktioniert aber nur sinnvoll asynchron)
# print(get_content())