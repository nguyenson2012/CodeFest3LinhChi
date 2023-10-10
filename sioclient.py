import asyncio
import socketio
import setproctitle
import sys
from datetime import datetime

CF_GAME_TITLE = 'Ну, погоди!'
CF_SERVER_URL = 'http://localhost/'
CF_DEMO_KEY = 'codefest-srv  | [2023-10-10T04:04:51.933Z] WRN/  **** YOUR NEW DEMO KEY: 0f4eb988-dcc9-4d5c-97ab-2b9d3df5dd5c ****'
CF_GAME_ID = 'b96d6fb5-d57f-4360-98b7-6966fc078f3b'
CF_PLAYER_1_ID = 'player1-xxx'
CF_PLAYER_2_ID = 'player2-xxx'
CF_EVENT_JOINGAME = 'join game'
CF_EVENT_POLLING = 'ticktack player'

def plog(msg):
    print(datetime.now(), CF_GAME_TITLE, msg)

setproctitle.setproctitle(CF_GAME_TITLE)


player = input('Please select player (1/2) ')
if player == '1':
    player = CF_PLAYER_1_ID
elif player == '2':
    player = CF_PLAYER_2_ID
else:
    plog('player undefined, exit!')
    quit()

sio = socketio.AsyncClient()

@sio.event
async def connect():
    plog(f'connection established with {CF_SERVER_URL}')
    await sio.emit(CF_EVENT_JOINGAME, {
        'game_id': CF_GAME_ID,
        'player_id': player
    })

@sio.event
async def my_message(data):
    plog(f'message received with {data}')
    await sio.emit('my response', {'response': 'my response'})
    return 'Ready', player

@sio.event
async def disconnect():
    plog('disconnected from server')


async def on_receive():
    try:
        event = await sio.receive()
    except Exception as ex:
        plog(f'Exception {ex} waiting for event')
    else:
        plog('received event:', event)

async def on_join_game(resp):
    plog(f'on_join_game {resp}')

async def on_polling(resp):
    plog(f'on_polling {resp}')


async def main():
    # task = sio.start_background_task(on_receive)
    sio.on(CF_EVENT_JOINGAME, on_join_game)
    sio.on(CF_EVENT_POLLING, on_polling)
    await sio.connect(CF_SERVER_URL)
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())