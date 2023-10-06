import asyncio
import socketio
import setproctitle
import sys
from datetime import datetime

CF_GAME_TITLE = 'Ну, погоди!'
CF_SERVER_URL = 'http://localhost/'
CF_GAME_ID = '2b09317b-6f64-4e51-8683-c92bbc26be6f'
CF_PLAYER_1_ID = 'player1-xxx'
CF_PLAYER_2_ID = 'player2-xxx'

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
    await sio.emit('join game', {
        'game_id': CF_GAME_ID,
        'player_id': player
    })

@sio.event
async def my_message(data):
    plog(f'message received with {data}')
    await sio.emit('my response', {'response': 'my response'})
    return 'Ready', player

# @sio.on
# async def on_join(msg)

@sio.event
async def disconnect():
    plog('disconnected from server')

async def main():
    await sio.connect(CF_SERVER_URL)
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
