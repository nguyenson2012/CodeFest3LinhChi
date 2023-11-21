"""
    config.py
"""
from datetime import datetime
from enum import Enum
import logging

"""
    codefest-srv  | [2023-10-16T06:42:33.522Z] WRN/  **** YOUR NEW DEMO KEY: b1693a74-1e63-4424-8d32-6c45a4b30dfc ****
"""

class ServerUri:
    URL_LOCAL: str = 'http://localhost/'
    URL_CONTEST: str = 'http://192.168.0.x/'

class DemoKey:
    LONG_LAPTOP_1020 = 'b1693a74-1e63-4424-8d32-6c45a4b30dfc'
    LONG_PC_1103 = 'cc439bc0-76fe-4006-b2f3-97b04aad5be0'
    LONG_PC_1117 = '35007977-2739-4e02-8d7b-ff568b2817a8'
    TU_LAPTOP = '55761bcb-e57c-4e73-84ca-545a852b40a4'

class CFGameMode(Enum):
    MODE_TRAINING = 0
    MODE_FIGHTING = 1

class CFConfig:

    class Game:

        TITLE: str = '3 Tin Elephants'
        MODE: Enum = CFGameMode.MODE_TRAINING
        W_WIDTH = 960
        W_HEIGHT = 480
        IMAGE = './data/3TinElephants.png'
        TIMEOUT = 200 # miliseconds

    class Server:
        URL: str = ServerUri.URL_LOCAL                           # Change to actual server URL during contest
        DEMO_KEY: str = DemoKey.LONG_PC_1117                     # Change to actual key during contest
        PLAYER_1_ID: str = 'player1-xxx'
        PLAYER_2_ID: str = 'player2-xxx'

    class Event:
        # player send action
        ACT_JOIN: str = 'join game'
        ACT_DRIVE: str = 'drive player'
        ACT_TAUNT: str = 'player speak'
        # msg received from server
        ON_BEAT: str = 'ticktack player'
        ON_JOIN: str = 'join game'
        ON_UPDATE: str = 'update game'
        ON_BOMB_SHOWN: str = 'show bomb'
        ON_BOMB_EXPLODED: str = 'detonate bomb'
        ON_BOMB_HIT: str = 'hit bomb'
        ON_MOVING_BANNED: str = 'moving banned'
        ON_GAME_TRAINING_STOP: str = 'stop training'
        # Sub event from 'ticktack player'
        ON_GAME_START: str = 'start-game'
        ON_MID_GAME: str = 'update-data'
        ON_PLAYER_MOVE_START: str = 'player:start-moving'
        ON_PLAYER_MOVE_STOP: str = 'player:stop-moving'
        ON_PLAYER_ISOLATED: str = 'player:be-isolated'
        ON_PLAYER_MOVE_BANNED: str = 'player:moving-banned'
        ON_PLAYER_PRISON_OUT: str ='player:back-to-playground'

    class MoveSet:
        LEFT: str = '1'
        RIGHT: str = '2'
        UP: str = '3'
        DOWN: str = '4'
        BOMB: str = 'b'
        STOP: str = 'x'


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'debug_{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
def plog(msg):
    logging.info(msg)
