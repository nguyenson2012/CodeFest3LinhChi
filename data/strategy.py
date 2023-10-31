"""
    strat_dummy.py
"""
from config.config import CFConfig as cf
from random import randint
import math

from core.game_state import GameState


def get_next_move_by_strategy(time_remain=None,map_json=None, player_id=None):
    if map_json is None:
        return cf.MoveSet.STOP
    #
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]
    converted_state = GameState(map_json)
    map_info = converted_state.map_info
    current_player = next((player for player in map_info.players if player.id == player_id), None)
    bombNearPlayer = check_bomb_near_player(map_info.bombs, current_player.currentPosition)
    if (bombNearPlayer):
        return againstBomb(current_player.currentPosition, map_info.bombs)
    if (time_remain > 90):
        # bomb the wall, choose eat spoils
        if (need_break_balk_around(map_info.map, current_player.currentPosition)):
            # call function to bomb the nearest balk
            return MOVES[randint(0, len(MOVES) - 1)]
        else:
            # eat spoil in radius 3
            return MOVES[randint(0, len(MOVES) - 1)]
    else:
        # choose attach gst egg
        return MOVES[randint(0, len(MOVES) - 1)]

    return MOVES[randint(0, len(MOVES) - 1)]

def check_bomb_near_player(bombs, currentPos):
    bombNums = 0
    for bomb in bombs:
        if (math.sqrt((bomb.row - currentPos.row) * (bomb.row - currentPos.row) + (bomb.col - currentPos.col) * (bomb.col - currentPos.col)) <= 16):
            bombNums += 1
        if bombNums > 3:
            return True
    return False


def need_break_balk_around(map, current_pos):
    balk_nums = 0
    for i in range(-3,3):
        for j in range(-3,3):
            if (current_pos.row + i < 0 or current_pos.col + j < 0):
                continue
            else:
                if (map[current_pos.row + i][current_pos.col +j] == 2):
                    balk_nums+=1
    if (balk_nums > 18):
        return True
    return False

def againstBomb(currentPos, bombs):
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]
    return MOVES[randint(0, len(MOVES) - 1)]

    
