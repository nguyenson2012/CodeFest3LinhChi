"""
    strat_dummy.py
"""
from config.config import CFConfig as cf
from random import randint


def get_next_move(map_json=None):
    if map_json is None:
        return cf.MoveSet.STOP
    #
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]

    return MOVES[randint(0, len(MOVES) - 1)]
