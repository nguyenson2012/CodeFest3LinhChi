"""
    strat_dummy.py
"""
from random import randint
from typing import List

from config.config import CFConfig as cf, plog
from connection.sioclient import CFSocket
from data.map import SpoilType, TerrainType
from core.game_state import GameState, MapSize, Player
from core.algorithm.common.a_star_search import a_star_search
from core.tools.converter import coordinates_to_directions
from core.tools.time_counter import measure_time


# ======================================================================================

"""
    Map transform
"""

class ExplosionMap:
    EXPLOSION_DURATION = 700
    COUNTDOWN_DURATION = 2000
    CROSSABLE_DURATION = 600

    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.data = [[0] * cols for _ in range(rows)]
        assert len(self.data) == self.rows
        assert len(self.data[0]) == self.cols
        self.timestamp = 0

    def update_new_bomb(self, games: GameState):
        bombs = games.map_info.bombs
        self.timestamp = games.timestamp

        # clear exploded cells
        for row in self.data:
            for i in range(self.cols):
                if row[i] + self.COUNTDOWN_DURATION + self.EXPLOSION_DURATION < self.timestamp:
                    row[i] = 0

        # add new cells in bomb's range
        for bomb in bombs:
            explosions = expand_by_lines_plus_self((bomb.col, bomb.row), bomb.power, games.map_info.size)
            for col, row in explosions:
                self.data[row][col] = bomb.createdAt

# keep the state throughout the game
global explosions; explosions = None


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


def is_near_cell_type(pos: tuple, maps, msize: MapSize, type: int) -> bool:
    near_cells = expand_by_lines(pos, 1, msize)
    return type in [maps[y][x] for x, y in near_cells]


# ======================================================================================

"""
    Strategy
"""

SAFE_ROAD = [
    TerrainType.ROAD.value,
    TerrainType.ROAD_WITH_EGG.value + SpoilType.SPEED_EGG.value,
    TerrainType.ROAD_WITH_EGG.value + SpoilType.ATTACH_EGG.value,
    TerrainType.ROAD_WITH_EGG.value + SpoilType.DELAY_EGG.value,
    TerrainType.ROAD_WITH_EGG.value + SpoilType.MYSTICS.value
]


def plant_bomb(pos: tuple, maps, msize: MapSize):
    escapable = False
    near_cells = expand_by_lines(pos, 1, msize)
    for x, y in near_cells:
        if maps[y][x] in SAFE_ROAD:
            escapable = True
            break
    if not escapable: # no near cell is safe, no bomb placed
        return None
    return [cf.MoveSet.BOMB]


def find_path_to(maps, pos: tuple, locations, traversable: List, path_limit: int):
    # skip long path
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


def update_map_with_object(client: CFSocket, explosions: ExplosionMap):
    maps = client.games.map_info.map
    rows, cols = (client.games.map_info.size.rows, client.games.map_info.size.cols)
    current_time = client.games.timestamp
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    pox, poy = (client.player_other.currentPosition.col, client.player_other.currentPosition.row)

    # this map objects should be mutually exclusive
    maps[poy][pox] = TerrainType.ROAD_WITH_OTHER_PLAYER.value

    for bomb in client.games.map_info.bombs:
        maps[bomb.row][bomb.col] = TerrainType.ROAD_WITH_BOMB.value
        if (bomb.row, bomb.col) == (py, px):
            # need to override bomb with bomb_and_player after dropping bomb for traversable points
            maps[py][px] = TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value

    for egg in client.games.map_info.spoils:
        # ROAD_WITH_EGG + SPEED_EGG
        # ROAD_WITH_EGG + ATTACH_EGG
        # ROAD_WITH_EGG + DELAY_EGG
        # ROAD_WITH_EGG + MYSTICS
        maps[egg.row][egg.col] = TerrainType.ROAD_WITH_EGG.value + egg.spoil_type


    # override traversable points with explosion, this cells are prediction and can be overlapped with eggs & players
    for row in range(rows):
        for col in range(cols):
            if explosions.data[row][col] == 0:
                continue
            bomb_created = explosions.data[row][col]
            if (bomb_created <= current_time <= bomb_created + explosions.CROSSABLE_DURATION
                and maps[row][col] in SAFE_ROAD):
                maps[row][col] = TerrainType.ROAD_WITH_COUNTDOWN.value
            if (bomb_created + explosions.CROSSABLE_DURATION < current_time
                and maps[row][col] in SAFE_ROAD):
                maps[row][col] = TerrainType.ROAD_WITH_EXPLOSION.value

    # debugging only
    mstr = ',\n'.join([str(row) for row in client.games.map_info.map])
    plog(f'Maps: player{(px, py)} opponent{(pox, poy)}\n{mstr}')


# ======================================================================================

"""
    Actions
"""
def find_nearest_buff_egg(client: CFSocket, maxsteps: int):
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    maps = client.games.map_info.map

    egg_locations = []
    for egg in client.games.map_info.spoils:
        if egg.spoil_type in [
            SpoilType.SPEED_EGG.value,
            SpoilType.ATTACH_EGG.value,
            SpoilType.DELAY_EGG.value
        ]:
            egg_locations.append((egg.col, egg.row))
    if egg_locations == []:
        return None

    return find_path_to(maps, (px, py), egg_locations, SAFE_ROAD, maxsteps)


def find_nearest_mystic_egg(client: CFSocket, maxsteps: int):
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    maps = client.games.map_info.map

    mystic_locations = []
    for egg in client.games.map_info.spoils:
        if egg.spoil_type == SpoilType.MYSTICS.value:
            mystic_locations.append((egg.col, egg.row))
    if mystic_locations == []:
        return None

    return find_path_to(maps, (px, py), mystic_locations, SAFE_ROAD, maxsteps)


def plant_bomb_near_balk(client: CFSocket, maxsteps: int):
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    msize = client.games.map_info.size
    maps = client.games.map_info.map

    def is_near_balk(pos: tuple):
        return is_near_cell_type(pos, maps, msize, TerrainType.BALK.value)

    if is_near_balk((px, py)):
        return plant_bomb((px, py), maps, msize) # [cf.MoveSet.BOMB]

    bombable_locations = []
    for row in range(msize.rows):
        for col in range(msize.cols):
            if maps[row][col] in SAFE_ROAD and is_near_balk((col, row)):
                bombable_locations.append((col, row))
    if bombable_locations == []:
            return None

    return find_path_to(maps, (px, py), bombable_locations, SAFE_ROAD, maxsteps)


def plant_bomb_near_GSTegg(client: CFSocket, maxsteps: int):
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    msize = client.games.map_info.size
    maps = client.games.map_info.map
    enemy_egg = [x for x in client.games.map_info.dragonEggGSTArray if x.id != client.player_id][0]
    ex, ey = (enemy_egg.col, enemy_egg.row)

    def is_near_gstegg(pos: tuple):
        # is_near_cell_type(pos, maps, msize, TerrainType.GST_DRAGON_EDGE.value)
        # enemy egg only
        x, y = pos
        if (abs(x - ex) == 1 and abs(y - ey) == 0) or (abs(x - ex) == 0 and abs(y - ey) == 1):
            return True
        return False

    if is_near_gstegg((px, py)):
        return plant_bomb((px, py), maps, msize) # [cf.MoveSet.BOMB]

    bombable_locations = []
    for row in range(msize.rows):
        for col in range(msize.cols):
            if maps[row][col] == TerrainType.ROAD.value and is_near_gstegg((col, row)):
                bombable_locations.append((col, row))
    if bombable_locations == []:
            return None

    return find_path_to(maps, (px, py), bombable_locations, SAFE_ROAD, maxsteps)


def move_away_from_bomb(client: CFSocket, maxsteps: int):
    px, py = (client.player.currentPosition.col, client.player.currentPosition.row)
    msize = client.games.map_info.size
    maps = client.games.map_info.map

    # skip if not in explosion range
    if maps[py][px] not in [
        TerrainType.ROAD_WITH_BOMB.value,
        TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value,
        TerrainType.ROAD_WITH_EXPLOSION.value,
        TerrainType.ROAD_WITH_COUNTDOWN.value
        ]:
        return None

    safe_locations = []
    for row in range(msize.rows):
        for col in range(msize.cols):
            if maps[row][col] in SAFE_ROAD:
                safe_locations.append((col, row))
    # fire in the hole
    if safe_locations == []:
        return None

    # Excluded cells with player from the escape path
    return find_path_to(
        maps, (px, py), safe_locations,
        SAFE_ROAD + [TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value, TerrainType.ROAD_WITH_COUNTDOWN.value],
        maxsteps
    )


# ======================================================================================

def get_next_move_random():
    """
        Random strategy
    """
    MOVES = [
        cf.MoveSet.UP, cf.MoveSet.DOWN, cf.MoveSet.LEFT, cf.MoveSet.RIGHT, cf.MoveSet.BOMB, cf.MoveSet.STOP
    ]
    return MOVES[randint(0, len(MOVES) - 1)]

def get_directions_from_input():
    """
        From console input, for debugging
    """
    return input('Directions /[1234xb]\{n\}/: ')



ACTION_MAP = [
    (move_away_from_bomb, 7),
    (find_nearest_buff_egg, 9),
    (plant_bomb_near_balk, 9),
    (find_nearest_mystic_egg, 12),
    # try again at longer range
    (plant_bomb_near_balk, 45),
    (find_nearest_buff_egg, 45),
    (plant_bomb_near_GSTegg, 50),
]

@measure_time
def get_next_move(client: CFSocket):
    """
        Action by priority
    """
    if client.games is None:
        return cf.MoveSet.STOP

    # instantiate first time only
    global explosions
    if explosions == None:
        explosions = ExplosionMap(client.games.map_info.size.rows, client.games.map_info.size.cols)

    explosions.update_new_bomb(client.games)
    update_map_with_object(client, explosions)


    next_move = None
    for action, steps in ACTION_MAP:
        next_move = action(client, steps)
        if next_move != None:
            plog(f'{action}, {steps} --> {next_move}')
            return ''.join(next_move)
    else:
        # if no action available return stop
        return cf.MoveSet.STOP
