"""
    strat_dummy.py
"""
from config import CFConfig as cf, plog
from enum import Enum
from random import randint


class TerrainType(Enum):
    ROAD = 0
    WALL = 1
    BALK = 2
    TELEPORT_GATE = 3
    QUARANTINE_PLACE = 4
    GST_DRAGON_EDGE = 5

class ItemType(Enum):
    NOTHING = 0
    PLAYER = 1
    BOMB = 2
    EGG = 3

def get_next_move(map_json = None):
    if map_json == None:
        return cf.MoveSet.STOP
    #
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]

    return MOVES[randint(0, len(MOVES) -1)]
