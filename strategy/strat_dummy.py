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


# ======================================================================================

"""
    Map transform
"""

class ExplosionMap:
    EXPLOSION_DURATION = 650

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
                if row[i] < self.timestamp:
                    row[i] = 0

        # add new cells in bomb's range
        for bomb in bombs:
            player:Player = [player for player in games.map_info.players if player.id == bomb.playerId][0]
            explosions = expand_by_lines_plus_self((bomb.col, bomb.row), player.power, games.map_info.size)
            for col, row in explosions:
                self.data[row][col] = self.timestamp + bomb.remainTime + self.EXPLOSION_DURATION

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
    bomb_path = [pos]
    near_cells = expand_by_lines(pos, 1, msize)
    for x, y in near_cells:
        if maps[y][x] in SAFE_ROAD:
            bomb_path.append((x, y))
            break

    directions = coordinates_to_directions(bomb_path)
    moves = [cf.MoveSet.BOMB]
    moves += [str(x) for x in directions] + [cf.MoveSet.STOP]
    return moves


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


def update_map_with_object(games: GameState, player: Player, player_other: Player, explosions: ExplosionMap):
    maps = games.map_info.map
    rows, cols = (games.map_info.size.rows, games.map_info.size.cols)
    px, py = (player.currentPosition.col, player.currentPosition.row)
    pox, poy = (player_other.currentPosition.col, player_other.currentPosition.row)
    maps[poy][pox] = TerrainType.ROAD_WITH_OTHER_PLAYER.value

    for bomb in games.map_info.bombs:
        maps[bomb.row][bomb.col] = TerrainType.ROAD_WITH_BOMB.value
        if (bomb.row, bomb.col) == (py, px):
            # need to override bomb with bomb_and_player after dropping bomb for traversable points
            maps[py][px] = TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value

    for row in range(rows):
        for col in range(cols):
            if explosions.data[row][col] > 0:
                if maps[row][col] in SAFE_ROAD:
                    # override traversable points with explosion
                    maps[row][col] = TerrainType.ROAD_WITH_EXPLOSION.value


    for egg in games.map_info.spoils:
        # ROAD_WITH_EGG + SPEED_EGG
        # ROAD_WITH_EGG + ATTACH_EGG
        # ROAD_WITH_EGG + DELAY_EGG
        # ROAD_WITH_EGG + MYSTICS
        maps[egg.row][egg.col] = TerrainType.ROAD_WITH_EGG.value + egg.spoil_type

    mstr = ',\n'.join([str(row) for row in games.map_info.map])
    plog(f'Maps: player{(px, py)} opponent{(pox, poy)}\n{mstr}')


# ======================================================================================

"""
    Actions
"""
def find_nearest_buff_egg(games: GameState, player: Player, maxsteps: int):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    maps = games.map_info.map

    egg_locations = []
    for egg in games.map_info.spoils:
        if egg.spoil_type in [
            SpoilType.SPEED_EGG.value,
            SpoilType.ATTACH_EGG.value,
            SpoilType.DELAY_EGG.value
        ]:
            egg_locations.append((egg.col, egg.row))
    if egg_locations == []:
        return None

    return find_path_to(maps, (px, py), egg_locations, SAFE_ROAD, maxsteps)


def find_nearest_mystic_egg(games: GameState, player: Player, maxsteps: int):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    maps = games.map_info.map

    mystic_locations = []
    for egg in games.map_info.spoils:
        if egg.spoil_type == SpoilType.MYSTICS.value:
            mystic_locations.append((egg.col, egg.row))
    if mystic_locations == []:
        return None

    return find_path_to(maps, (px, py), mystic_locations, SAFE_ROAD, maxsteps)


def plant_bomb_near_balk(games: GameState, player: Player, maxsteps: int):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

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


def plant_bomb_near_GSTegg(games: GameState, player: Player, maxsteps: int):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map
    enemy_egg = [x for x in games.map_info.dragonEggGSTArray if x.id != player.id][0]
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


def move_away_from_bomb(games: GameState, player: Player, maxsteps: int):
    px, py = (player.currentPosition.col, player.currentPosition.row)
    msize = games.map_info.size
    maps = games.map_info.map

    # skip if not in explosion range
    if maps[py][px] not in [TerrainType.ROAD_WITH_BOMB.value, TerrainType.ROAD_WITH_EXPLOSION.value, TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value]:
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
    return find_path_to(maps, (px, py), safe_locations, SAFE_ROAD + [TerrainType.ROAD_WITH_BOMB_AND_PLAYER.value] , maxsteps)


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
    (move_away_from_bomb, 5),
    (find_nearest_buff_egg, 9),
    (plant_bomb_near_balk, 9),
    (find_nearest_mystic_egg, 12),
    # try again at longer range
    (plant_bomb_near_balk, 30),
    (find_nearest_buff_egg, 30),
    (plant_bomb_near_GSTegg, 30),
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
    player_other: Player = [x for x in games.map_info.players if x.id != playerid][0]

    # instantiate first time only
    global explosions
    if explosions == None:
        explosions = ExplosionMap(games.map_info.size.rows, games.map_info.size.cols)

    explosions.update_new_bomb(games)
    update_map_with_object(games, player, player_other, explosions)


    next_move = None
    for action, steps in ACTION_MAP:
        next_move = action(games, player, steps)
        if next_move != None:
            plog(f'{action}, {steps} --> {next_move}')
            return ''.join(next_move)
    else:
        # if no action available return stop
        return cf.MoveSet.STOP
