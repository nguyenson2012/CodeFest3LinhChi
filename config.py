"""
    config.py
"""
from datetime import datetime
from enum import Enum

"""
    codefest-srv  | [2023-10-16T06:42:33.522Z] WRN/  **** YOUR NEW DEMO KEY: b1693a74-1e63-4424-8d32-6c45a4b30dfc ****
"""

class CFGameMode(Enum):
    MODE_TRAINING = 0
    MODE_FIGHTING = 1

class CFConfig:

    class Game:

        TITLE: str = '3 Tin Elephants'
        MODE: Enum = CFGameMode.MODE_TRAINING
        W_WIDTH = 260
        W_HEIGHT = 140

    class Server:
        URL: str = 'http://localhost/'                           # Change to actual server URL when in contest
        HREF_TRAINING: str = '/training/login'
        HREF_FIGHTING: str = '/fighting'
        HREF_GAME_TRAINING: str = '/training/stage/'
        # DEMO_KEY: str = 'd8b0c0bc-3e08-4751-bc16-e5a85e4f1074'   # Modify this value based on running environment # PC Steel Dragon
        DEMO_KEY: str = 'b1693a74-1e63-4424-8d32-6c45a4b30dfc'     # Laptop Surface
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
        ON_MOVING_BANNED: str = 'moving banned'
        ON_GAME_TRAINING_STOP: str = 'stop training'
        # Sub event from 'ticktack player'
        ON_GAME_START: str = 'start-game'

    class MoveSet:
        LEFT: str = '1'
        RIGHT: str = '2'
        UP: str = '3'
        DOWN: str = '4'
        BOMB: str = 'b'
        STOP: str = 'x'

def plog(msg):
    print(datetime.now(), CFConfig.Game.TITLE, msg)
