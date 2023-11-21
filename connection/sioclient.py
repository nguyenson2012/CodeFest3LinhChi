"""
    sioclient.py
"""
import socketio
from config.config import CFConfig as cf, plog
from core.game_state import GameState, Player
import threading
from time import sleep
from random import randint

TAUNTS = ['t1', 't2', 'i1', 'i2', 'i3', 'i4', 'i5', 'i6', 'i7', 'i8']

class CFSocket:
    """
        Class in charged of communication with server.
    """

    def __init__(self, gameid, playerid) -> None:
        self.game_id: str = gameid
        self.player_id_start: str = playerid
        self.player_id: str = None

        self.sio: socketio.Client = socketio.Client()
        self.sio.on('*', self.on_event)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)

        self.is_joined: bool = False
        self.is_startgame: bool = False
        self.is_midgame: bool = False
        self.is_stoptraining: bool = False
        self.is_moving: bool = False
        self.moving_count: int = 0

        self.lock = threading.Lock()
        self.map_json: dict = None
        self.games: GameState = None
        self.player: Player = None
        self.player_other: Player = None


    # start connection & wait for event
    def connect_and_join(self):
        self.sio.connect(cf.Server.URL)
        retry: int = 0
        while retry < 10:
            sleep(0.2)
            if self.sio.connected:
                self.join_game()
                break
            retry += 1


    def quite_game(self):
        self.sio.disconnect()


    # Listeners
    def on_connect(self):
        plog(f'<on_connect> connection established with {cf.Server.URL}')


    def on_disconnect(self):
        plog(f'<on_disconnect> disconnected from server {cf.Server.URL}')


    # Join a game
    def join_game(self):
        self.sio.emit(cf.Event.ACT_JOIN, {
            'game_id': self.game_id,
            'player_id': self.player_id_start
        })
        plog(f'<emit> <{cf.Event.ACT_JOIN}> with {self.game_id} & {self.player_id_start}')


    # Move the voi
    def direct_player(self, direct: str):
        '''
            1: LEFT 2: RIGHT 3: UP 4: DOWN
            b: bomb x: stop moving 
        '''
        if self.is_moving or self.moving_count > 0:
            plog(f'<direct_player> player moving, not sending directions! moving_count: {self.moving_count}')
            return

        # limit to 4 moves, to better avoiding new bomb
        if len(direct) > 4:
            direct = direct[:4]

        self.moving_count = (
            direct.count(cf.MoveSet.UP) +
            direct.count(cf.MoveSet.DOWN) +
            direct.count(cf.MoveSet.LEFT) +
            direct.count(cf.MoveSet.RIGHT)
        )

        try:
            self.sio.emit(cf.Event.ACT_DRIVE, {
                'direction': direct
            })
            plog(f'<emit> <{cf.Event.ACT_DRIVE}> {self.player_id_start} with {direct}')
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
        plog(f'<emit> {self.player_id_start} <{cf.Event.ACT_TAUNT}> with {speak}')


    def update_map(self):
        if self.map_json == None:
            return

        # update game state
        if self.map_json['tag'] == cf.Event.ON_GAME_START:
            self.is_startgame = True
        elif self.map_json['tag'] == cf.Event.ON_MID_GAME:
            self.is_midgame = True

        # update game info
        del self.games
        self.games = GameState(data=self.map_json)

        # player and other
        assert len(self.games.map_info.players) == 2
        self.player = [x for x in self.games.map_info.players if x.id == self.player_id][0]
        self.player_other = [x for x in self.games.map_info.players if x.id != self.player_id][0]

        # move sync
        if self.games.tag == cf.Event.ON_PLAYER_MOVE_START and self.games.player_id == self.player_id:
            self.is_moving = True

        elif self.games.tag == cf.Event.ON_PLAYER_MOVE_STOP and self.games.player_id == self.player_id:
            self.moving_count -= 1
            plog(f'<update_map> moving_count: {self.moving_count}')
            # player stop without start, due to collison or blocked move
            if self.is_moving == False:
                self.moving_count = 0
                plog(f'<update_map> moving_count reset (collision???): {self.moving_count}')
            self.is_moving = False

        elif self.games.tag == cf.Event.ON_PLAYER_MOVE_BANNED and self.games.player_id == self.player_id:
            self.moving_count = 0
            plog(f'<update_map> moving_count reset (move banned): {self.moving_count}')

        # isolation
        elif self.games.tag in [cf.Event.ON_PLAYER_ISOLATED, cf.Event.ON_PLAYER_PRISON_OUT] and self.games.player_id == self.player_id:
            self.is_moving = False
            self.moving_count = 0
            plog(f'<update_map> moving_count reset (prison in/out): {self.moving_count}')


    # catch all
    def on_event(self, *args):
        if args[0] == cf.Event.ON_BEAT:
            plog(f'<on_event> {args[0]} {args[1]["tag"]} {args[1]["timestamp"]} {args[1].get("player_id")}')
            self.lock.acquire()
            self.map_json = args[1]
            self.update_map()
            self.lock.release()
            return

        plog(f'<on_event> {args}')
        if args[0] == cf.Event.ON_JOIN:
            self.is_joined = True
            if self.player_id == None and self.player_id_start[:11] == args[1]['player_id'][:11]:
                self.player_id = args[1]['player_id']
                plog(f'<on_event> {self.player_id_start} joined as {self.player_id}')
        elif args[0] == cf.Event.ON_GAME_TRAINING_STOP:
            self.is_stoptraining = True
        elif args[0] == cf.Event.ON_BOMB_HIT and self.player_other.id in args[1]['hitBomb']:
            self.taunt_player(TAUNTS[randint(0, len(TAUNTS) - 1)])
        else:
            pass
