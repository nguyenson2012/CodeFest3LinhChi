"""
    strat_dummy.py
"""
from config.config import CFConfig as cf, plog
from random import randint
from core.game_state import GameState, MapSize, Player
from typing import List
from data.map import SpoilType, TerrainType
from core.algorithm.find_path_best_spoil import find_path_best_spoil
from core.tools.converter import coordinates_to_directions
from core.tools.time_counter import measure_time

MAX_STEPS = 7


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


def is_near_cell(pos: tuple, maps, msize: MapSize, type: int) -> bool:
    near_cells = expand_by_lines(pos, 1, msize)
    return type in [maps[y][x] for x, y in near_cells]


def get_path_by(maps, pos: tuple, locations, traversable: List):
    best_path = find_path_best_spoil(maps, pos, locations, traversable)
    plog(best_path)
    if best_path == None:
        return None

    directions = coordinates_to_directions(best_path)
    if len(directions) > MAX_STEPS:
        return None

    moves = [str(x) for x in directions]
    return moves

# ======================================================================================

"""
    Actions
"""
def find_nearest_spoil(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    maps = games.map_info.map

    # for spoil in games.map_info.spoils:
    #     plog(spoil)
    # plog(f'{px} {py}')
    spoil_locations = []
    for egg in games.map_info.spoils:
        if egg.spoil_type in [SpoilType.SPEED_EGG.value, SpoilType.ATTACH_EGG.value, SpoilType.DELAY_EGG.value, SpoilType.MYSTICS.value]:
            spoil_locations.append((egg.col, egg.row))
    if spoil_locations == []:
        return None

    return get_path_by(maps, (px, py), spoil_locations, [TerrainType.ROAD.value])


def plant_bomb_near_balk(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

    def is_near_balk(pos: tuple):
        return is_near_cell(pos, maps, msize, TerrainType.BALK.value)

    if is_near_balk((px, py)):
        return [cf.MoveSet.BOMB]

    bombable_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value and is_near_balk((x, y)):
                bombable_locations.append((x, y))
    if bombable_locations == []:
            return None

    return get_path_by(maps, (px, py), bombable_locations, [TerrainType.ROAD.value])


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
        return [cf.MoveSet.BOMB]

    bombable_locations = []
    bombable_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value and is_near_gstegg((x, y)):
                bombable_locations.append((x, y))
    if bombable_locations == []:
            return None

    return get_path_by(maps, (px, py), bombable_locations, [TerrainType.ROAD.value])


def move_away_from_bomb(games: GameState, player: Player):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

    # update bombs with expolsion radius
    bomb_cells = set()
    for bomb in games.map_info.bombs:
        player:Player = [player for player in games.map_info.players if player.id == bomb.playerId][0]
        bomb_cells.update(expand_by_lines_plus_self((bomb.col, bomb.row), player.power, games.map_info.size))

    near_cells = set(expand_by_lines_plus_self((px, py), 1, msize))

    plog(bomb_cells)
    plog(near_cells)
    plog(near_cells.isdisjoint(bomb_cells))
    plog(player)
    if near_cells.isdisjoint(bomb_cells):
        return None

    # Update map with dynamic objects
    for x, y in bomb_cells:
        maps[y][x] = TerrainType.ROAD_WITH_BOMB.value

    road_locations = []
    for y in range(msize.rows):
        for x in range(msize.cols):
            if maps[y][x] == TerrainType.ROAD.value:
                road_locations.append((x, y))
    plog(road_locations)
    if road_locations == []:
        return None

    # Excluded cells with player from the escape path
    return get_path_by(maps, (px, py), road_locations, [TerrainType.ROAD.value, TerrainType.ROAD_WITH_BOMB.value])


# ======================================================================================

def get_next_move_random():
    """
        Random strategy
    """
    return MOVES[randint(0, len(MOVES) - 1)]


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
    opx, opy = (opp_player.currentPosition.col, opp_player.currentPosition.row)
    # Opponent player position is non-traversable point
    games.map_info.map[opy][opx] = TerrainType.ROAD_WITH_PLAYER.value

    next_move = None
    for action in PRIORITIZED_ACTIONS:
        next_move = action(games, player)
        plog(f'{action}() {next_move}')
        if next_move != None:
            assert isinstance(next_move, List)
            assert len(next_move) > 0
            # Send only first move
            return next_move[0]
    else:
        # if no action return valid move
        return cf.MoveSet.STOP
