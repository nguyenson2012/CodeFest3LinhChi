"""
    sioclient.py
"""
import socketio
from config.config import CFConfig as cf, plog
import threading
from pygame.time import wait


class CFSocket:
    """
        Class in charged of communication with server.
    """

    def __init__(self, game, player) -> None:
        self.game_id: str = game
        self.player_id: str = player
        self.sio: socketio.Client = socketio.Client()
        self.sio.on('*', self.on_event)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.lock = threading.Lock()
        self.map_json: dict = None
        self.is_joined: bool = False
        self.is_startgame: bool = False
        self.is_midgame: bool = False
        self.is_stoptraining: bool = False

    # start connection & wait for event
    def sio_connect(self):
        self.sio.connect(cf.Server.URL)

    # end connection
    def sio_terminate(self):
        self.sio.disconnect()

    def is_connected(self) -> bool:
        return self.sio.connected

    # Listeners
    def on_connect(self):
        plog(f'<on_connect> connection established with {cf.Server.URL}')

    def on_disconnect(self):
        plog(f'<on_disconnect> disconnected from server {cf.Server.URL}')

    # Join a game
    def join_game(self):
        self.sio.emit(cf.Event.ACT_JOIN, {
            'game_id': self.game_id,
            'player_id': self.player_id
        })
        plog(f'<emit> <{cf.Event.ACT_JOIN}> with {self.game_id} & {self.player_id}')

    # Move the voi
    def direct_player(self, direct: str):
        '''
            1: LEFT 2: RIGHT 3: UP 4: DOWN
            b: bomb x: stop moving 
        '''
        try:
            self.sio.emit(cf.Event.ACT_DRIVE, {
                'direction': direct
            })
            plog(f'<emit> <{cf.Event.ACT_DRIVE}> {self.player_id} with {direct}')
        except socketio.exceptions.BadNamespaceError as ex:
            plog(f'{__file__} socketio BadNamespaceError: {ex}')

    # Taunt opponent
    def taunt_player(self, speak: str):
        '''
            command for message: 't1', 't2'
            command for icon: 'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8'
        '''
        self.sio.emit(cf.Event.ACT_TAUNT, {
            'command': speak
        })
        plog(f'<emit> {self.player_id} <{cf.Event.ACT_TAUNT}> with {speak}')


    def update_map(self):
        if self.map_json == None:
            return
        if self.map_json['tag'] == cf.Event.ON_GAME_START:
            self.is_startgame = True
        elif self.map_json['tag'] == cf.Event.ON_MID_GAME:
            self.is_midgame = True

    # catch all
    def on_event(self, *args):
        if args[0] == cf.Event.ON_BEAT:
            plog(f'<on_event> {args[0]} {args[1]["tag"]} {args[1]["timestamp"]}')
            self.lock.acquire()
            self.map_json = args[1]
            self.update_map()
            self.lock.release()
        elif args[0] == cf.Event.ON_JOIN:
            plog(f'<on_event> {args}')
            self.is_joined = True
        elif args[0] == cf.Event.ON_GAME_TRAINING_STOP:
            plog(f'<on_event> {args}')
            self.is_stoptraining = True
        else:
            plog(f'<on_event> {args}')


    # Should only use these functions outside of CFSocket
    def connect_and_join(self):
        self.sio_connect()
        retry: int = 0
        while retry < 10:
            wait(200)
            if self.is_connected():
                self.join_game()
                break
            retry += 1

    def quite_game(self):
        self.sio_terminate()
