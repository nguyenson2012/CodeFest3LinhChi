"""
    strat_dummy.py
"""
from config.config import CFConfig as cf, plog
from random import randint
from core.game_state import GameState, MapSize, Player
from typing import List
from data.map import SpoilType, TerrainType
from core.algorithm.common.a_star_search import a_star_search
from core.tools.converter import coordinates_to_directions
from core.tools.time_counter import measure_time


MOVES = [
    cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
]

# ======================================================================================

"""
    Map transform
"""

def expand_by_lines(pos: tuple, distance: int, msize: MapSize) -> List:
    exp_cells = []
    x, y = pos

    # col for x, row for y
    for i in range(1, distance+1):
        # LEFT
        if x - i >= 0:
            exp_cells.append((x - i, y))
        # RIGHT
        if x + i < msize.cols:
            exp_cells.append((x + i, y))
        # UP
        if y - i >= 0:
            exp_cells.append((x, y - i))
        # DOWN
        if y + i < msize.rows:
            exp_cells.append((x, y + i))
    return exp_cells


def expand_by_lines_plus_self(pos: tuple, distance: int, msize: MapSize) -> List:
    bomb_cells = []
    bomb_cells.append(pos)
    bomb_cells.extend(expand_by_lines(pos, distance, msize))
    return bomb_cells


def expand_by_lines_exclude_immovable(pos: tuple, distance: int, msize: MapSize, maps) -> List:
    cells = expand_by_lines_plus_self(pos, distance, msize)
    keeps = []
    for x, y in cells:
        if maps[y][x] in [
            TerrainType.ROAD.value,
            TerrainType.ROAD_WITH_BOMB.value,
            TerrainType.ROAD_WITH_EGG.value,
            TerrainType.ROAD_WITH_PLAYER.value
        ]:
            keeps.append((x, y))
    return keeps


def is_near_cell_type(pos: tuple, maps, msize: MapSize, type: int) -> bool:
    near_cells = expand_by_lines(pos, 1, msize)
    return type in [maps[y][x] for x, y in near_cells]


def plant_bomb(pos: tuple, maps, msize: MapSize):
    bomb_path = [pos]
    near_cells = expand_by_lines(pos, 1, msize)
    for x, y in near_cells:
        if maps[y][x] == TerrainType.ROAD.value:
            bomb_path.append((x, y))
            break

    directions = coordinates_to_directions(bomb_path)
    moves = [cf.MoveSet.BOMB]
    moves += [str(x) for x in directions]
    return moves


def find_path_to(maps, pos: tuple, locations, traversable: List, path_limit: int = cf.MaxSteps.MAX_STEPS):
    # a path which is too long is not practical when moving one by one
    shortest_path_length = path_limit + 1
    shortest_path = None

    for cell in locations:
        path = a_star_search(maps, pos, cell, traversable)
        if path and len(path) < shortest_path_length:
            shortest_path = path
            shortest_path_length = len(path)

    if shortest_path == None:
        return None

    # a_star_search() does not return start position
    shortest_path.insert(0, pos)
    assert len(shortest_path) > 1

    directions = coordinates_to_directions(shortest_path)
    assert len(directions) > 0

    moves = [str(x) for x in directions]
    return moves


def update_map_with_spoil_and_bomb(games: GameState, player: Player):
    maps = games.map_info.map

    bomb_cells = set()
    for bomb in games.map_info.bombs:
        player:Player = [player for player in games.map_info.players if player.id == bomb.playerId][0]
        bomb_cells.update(expand_by_lines_exclude_immovable((bomb.col, bomb.row), player.power, games.map_info.size, maps))

    # Update map with dynamic objects
    for x, y in bomb_cells:
        maps[y][x] = TerrainType.ROAD_WITH_BOMB.value

    spoil_locations = []
    for egg in games.map_info.spoils:
        if egg.spoil_type in [SpoilType.SPEED_EGG.value, SpoilType.ATTACH_EGG.value, SpoilType.DELAY_EGG.value, SpoilType.MYSTICS.value]:
            spoil_locations.append((egg.col, egg.row))
            maps[egg.row][egg.col] = TerrainType.ROAD_WITH_EGG.value


# ======================================================================================

"""
    Actions
"""
def find_nearest_spoil(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    maps = games.map_info.map

    spoil_locations = []
    for egg in games.map_info.spoils:
        if egg.spoil_type in [SpoilType.SPEED_EGG.value, SpoilType.ATTACH_EGG.value, SpoilType.DELAY_EGG.value, SpoilType.MYSTICS.value]:
            spoil_locations.append((egg.col, egg.row))
            maps[egg.row][egg.col] = TerrainType.ROAD_WITH_EGG.value
    if spoil_locations == []:
        return None

    return find_path_to(maps, (px, py), spoil_locations, [TerrainType.ROAD.value, TerrainType.ROAD_WITH_EGG.value], cf.MaxSteps.MAX_STEPS_COLLECT_SPOIL)


def plant_bomb_near_balk(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

    def is_near_balk(pos: tuple):
        return is_near_cell_type(pos, maps, msize, TerrainType.BALK.value)

    if is_near_balk((px, py)):
        return plant_bomb((px, py), maps, msize) # [cf.MoveSet.BOMB]

    bombable_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value and is_near_balk((x, y)):
                bombable_locations.append((x, y))
    if bombable_locations == []:
            return None

    return find_path_to(maps, (px, py), bombable_locations, [TerrainType.ROAD.value], cf.MaxSteps.MAX_STEPS_BOMB_BALK)


def plant_bomb_near_GSTegg(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map
    enemy_egg = [x for x in games.map_info.dragonEggGSTArray if x.id != player.id][0]
    ex, ey = (enemy_egg.col, enemy_egg.row)

    def is_near_gstegg(pos: tuple):
        x, y = pos
        if (abs(x - ex) == 1 and abs(y - ey) == 0) or (abs(x - ex) == 0 and abs(y - ey) == 1):
            return True
        return False

    if is_near_gstegg((px, py)):
        return plant_bomb((px, py), maps, msize) # [cf.MoveSet.BOMB]

    bombable_locations = []
    bombable_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value and is_near_gstegg((x, y)):
                bombable_locations.append((x, y))
    if bombable_locations == []:
            return None

    return find_path_to(maps, (px, py), bombable_locations, [TerrainType.ROAD.value], cf.MaxSteps.MAX_STEPS_BOMB_EGG)


def move_away_from_bomb(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

    # update bombs with expolsion radius
    bomb_cells = set()
    for bomb in games.map_info.bombs:
        player:Player = [player for player in games.map_info.players if player.id == bomb.playerId][0]
        bomb_cells.update(expand_by_lines_exclude_immovable((bomb.col, bomb.row), player.power, games.map_info.size, maps))

    near_cells = set(expand_by_lines_exclude_immovable((px, py), 1, msize, maps))
    is_overlapped_with_bomb = near_cells.isdisjoint(bomb_cells)

    if is_overlapped_with_bomb:
        return None

    # Update map with dynamic objects
    for x, y in bomb_cells:
        maps[y][x] = TerrainType.ROAD_WITH_BOMB.value

    road_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value:
                road_locations.append((x, y))
    if road_locations == []:
        return None

    # Excluded cells with player from the escape path
    return find_path_to(maps, (px, py), road_locations, [TerrainType.ROAD.value, TerrainType.ROAD_WITH_BOMB.value], cf.MaxSteps.MAX_STEPS_RUN_AWAY)


# ======================================================================================

def get_next_move_random():
    """
        Random strategy
    """
    return MOVES[randint(0, len(MOVES) - 1)]

def get_directions_from_input():
    """
        From console input, for debugging
    """
    return input('Directions /[1234xb]\{n\}/: ')



PRIORITIZED_ACTIONS = [
    move_away_from_bomb,
    find_nearest_spoil,
    plant_bomb_near_balk,
    plant_bomb_near_GSTegg
]

@measure_time
def get_next_move(playerid: str, map_json):
    """
        Action by priority
    """
    if map_json is None:
        return cf.MoveSet.STOP
    #
    games = GameState(data=map_json)
    player: Player = [x for x in games.map_info.players if x.id == playerid][0]
    opp_player: Player = [x for x in games.map_info.players if x.id != player.id][0]
    px, py = (player.currentPosition.col, player.currentPosition.row)
    opx, opy = (opp_player.currentPosition.col, opp_player.currentPosition.row)
    # Opponent player position is non-traversable point
    games.map_info.map[opy][opx] = TerrainType.ROAD_WITH_PLAYER.value

    next_move = None
    for action in PRIORITIZED_ACTIONS:
        next_move = action(games, player)
        if next_move != None:
            assert isinstance(next_move, List)
            assert len(next_move) > 0
            # Send only first move
            # return next_move[0]
            update_map_with_spoil_and_bomb(games, player)
            # mstr = ',\n'.join([str(row) for row in games.map_info.map])
            # plog(f'Maps: player{(px, py)} opponent{(opx, opy)}\n{mstr}')
            return ''.join(next_move)
    else:
        # if no action return valid move
        return cf.MoveSet.STOP
