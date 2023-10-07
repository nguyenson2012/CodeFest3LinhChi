import asyncio
import socketio
import setproctitle
import sys
from datetime import datetime

CF_GAME_TITLE = 'Ну, погоди!'

setproctitle.setproctitle(CF_GAME_TITLE)

CF_SERVER_URL = 'http://localhost/'

CF_GAME_ID = 'f0318ff4-6fca-4784-afc0-259e7bd59eda'

CF_PLAYER_ID = 'player1-xxx'

if len(sys.argv) > 1:
    if sys.argv[1] == '1':
        PLAYER_ID = 'player1-xxx'
    elif sys.argv[1] == '2':
        PLAYER_ID = 'player2-xxx'

def plog(msg):
    print(datetime.now(), CF_GAME_TITLE, msg)

sio = socketio.AsyncClient()

@sio.event
async def connect():
    plog(f'connection established with {CF_SERVER_URL}')
    await sio.emit('join game', {
        'game_id': CF_GAME_ID,
        'player_id': CF_PLAYER_ID
    })

@sio.event
async def my_message(data):
    plog(f'message received with {data}')
    await sio.emit('my response', {'response': 'my response'})
    return 'Ready', CF_PLAYER_ID

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
