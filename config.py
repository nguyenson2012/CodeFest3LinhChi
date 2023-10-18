"""
    config.py
"""
from datetime import datetime
import setproctitle
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

    class Server:
        URL: str = 'http://localhost/'
        HREF_TRAINING: str = '/training/login'
        HREF_FIGHTING: str = '/fighting'
        DEMO_KEY: str = 'b1693a74-1e63-4424-8d32-6c45a4b30dfc'
        PLAYER_1_ID: str = 'player1-xxx'
        PLAYER_2_ID: str = 'player2-xxx'

    class Event:
        JOIN: str = 'join game'
        BEAT: str = 'ticktack player'
        DRIVE: str = 'drive player'
        TAUNT: str = 'player speak'


def plog(msg):
    print(datetime.now(), CFConfig.Game.TITLE, msg)

setproctitle.setproctitle(CFConfig.Game.TITLE)
