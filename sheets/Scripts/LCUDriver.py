from lcu_driver import Connector

connector = Connector()

async def set_random_icon(connection, gameID):

    # make the request to set the icon
    response = await connection.request('GET', f'/lol-match-history/v1/games/{gameID}')

    if response.status == 200:
        # JSON-Inhalt abrufen
        content = await response.json()
        print(content)
    else:
        print(f'Fehler: {response.status}')

# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')
    # check if the user is already logged into his account
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Please login into your account to change your icon and restart the script...')
    else:
        print('fetching League Client data ...')
        await set_random_icon(connection, 7365236186)


# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    print('disconnected')

# starts the connector
connector.start()