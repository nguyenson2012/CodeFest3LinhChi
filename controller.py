from random import randint

from config.config import CFConfig as cf
from core.algorithm.find_path_best_spoil import find_path_best_spoil
from core.algorithm.find_path_toggle_bomb import find_path_toggle_bomb
from core.game_state import GameState
from config.converter import coordinates_to_directions
from data.map import ACTION, TerrainType


def get_next_move(player_id=None, map_json=None):
    if map_json is None or player_id is None:
        return cf.MoveSet.STOP

    action = ACTION.FIND_EAT_EGGS
    converted_state = GameState(map_json)
    map_info = converted_state.map_info
    #
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]

    if action == ACTION.FIND_EAT_EGGS:
        current_player = next((player for player in map_info.players if player.id == player_id), None)
        if current_player is None:
            return cf.MoveSet.STOP
        best_spoil_path = find_path_best_spoil(
            map_data=map_info.map,
            start_position=(
                current_player.currentPosition.row,
                current_player.currentPosition.column
            ),
            spoil_locations=list(map(lambda spoil: (spoil.row, spoil.col), map_info.spoils)),
            traversable_points=[TerrainType.ROAD.value, TerrainType.BALK.value]
        )
        path_to_spoil = []
        balk_pos = None
        for pos in best_spoil_path:
            if map_info.map[pos[0]][pos[1]] == TerrainType.ROAD.value:
                path_to_spoil += pos
            else:
                balk_pos = pos
                break
        # this function will represent a list of direction between 2 adjacent item
        direction_converted = coordinates_to_directions(path_to_spoil)

        if balk_pos is not None:
            direction_converted += cf.MoveSet.BOMB
            pos_bomb = path_to_spoil[-1]
            path_to_toggle = find_path_toggle_bomb(
                map_data=map_info.map,
                bomb_position=(pos_bomb[0], pos_bomb[1]),
                bomb_size=current_player.power,
                traversable_points=[TerrainType.ROAD.value, TerrainType.BALK.value]
            )
            if path_to_toggle is not None:
                direction_converted += coordinates_to_directions(find_path_toggle_bomb)
            else:
                direction_converted -= cf.MoveSet.BOMB
        return direction_converted
    elif action == ACTION.ATTACH_GST_EGGS:
        pass
    else:
        pass
    return MOVES[randint(0, len(MOVES) - 1)]
