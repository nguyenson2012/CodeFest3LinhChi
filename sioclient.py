"""
    sioclient.py
"""
import socketio
from config import CFConfig as cf, plog


class CFSocket:
    """
        Class in charged of communication with server.
    """
    game_id: str = None
    player_id: str = None
    sio: socketio.Client = None

    def __init__(self, game, player) -> None:
        self.game_id = game
        self.player_id = player
        self.sio = socketio.Client()
        self.sio.on('*', self.on_event)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)

    # Listeners
    def on_connect(self):
        plog(f'<on_connect> connection established with {cf.Server.URL}')
        plog(self.sio.namespaces)
        plog(self.sio.namespace_handlers)

    def on_disconnect(self):
        plog(f'<on_disconnect> disconnected from server {cf.Server.URL}')

    # catch all
    def on_event(self, *args):
        plog(f'<on_event> {args}')

    # Join a game
    def join_game(self):
        self.sio.emit(cf.Event.JOIN, {
            'game_id': self.game_id,
            'player_id': self.player_id
        })
        plog(f'<emit> <{cf.Event.JOIN}> with {self.game_id} & {self.player_id}')

    # Move the voi
    def direct_player(self, direct: str):
        '''
            1: LEFT 2: RIGHT 3: UP 4: DOWN
            b: bomb x: stop moving 
        '''
        self.sio.emit(cf.Event.DRIVE, {
            'direction': direct
        })
        plog(f'<emit> <{cf.Event.DRIVE}> {self.player_id} with {direct}')

    # Taunt opponent
    def taunt_player(self, speak: str):
        '''
            command for message: 't1', 't2'
            command for icon: 'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8'
        '''
        self.sio.emit(cf.Event.TAUNT, {
            'command': speak
        })
        plog(f'<emit> {self.player_id} <{cf.Event.TAUNT}> with {speak}')

    # end connection
    def sio_terminate(self):
        self.sio.disconnect()

    # start connection & wait for event
    def sio_connect(self):
        self.sio.connect(cf.Server.URL)

    def is_connected(self) -> bool:
        return self.sio.connected

    # Insert Jobs
    def run_job(self, job: any, *args):
        task = self.sio.start_background_task(job, *args)
        plog(task)

    # wait loop
    def sio_wait(self):
        self.sio.wait()
