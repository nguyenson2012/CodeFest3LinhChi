# Example usage:
import json

from core.algorithm.common.a_star_search import a_star_search
from core.algorithm.common.dijkstra_search import dijkstra_search
from core.algorithm.find_path_best_spoil import find_path_best_spoil
from core.algorithm.find_path_toggle_bomb import find_path_toggle_bomb
from core.game_state import GameState
from config.converter import coordinates_to_directions
from data.map import TerrainType


def print_game_state(game_state):
    print("GameState:")
    print("id:", game_state.id)
    print("timestamp:", game_state.timestamp)
    print("map_info:")
    print_map_info(game_state.map_info)
    print("tag:", game_state.tag)
    print("player_id:", game_state.player_id)
    print("gameRemainTime:", game_state.gameRemainTime)


def print_map_info(map_info):
    print("MapInfo:")
    print("size:")
    print_map_size(map_info.size)
    print("players:")
    for player in map_info.players:
        print_player(player)
    print("map:", map_info.map)
    print("bombs:")
    for bomb in map_info.bombs:
        print_bomb(bomb)
    print("spoils:")
    for spoil in map_info.spoils:
        print_spoil(spoil)
    print("gameStatus:", map_info.gameStatus)
    print("dragonEggGSTArray:")
    for dragon_egg_gst in map_info.dragonEggGSTArray:
        print_dragon_egg_gst(dragon_egg_gst)


def print_map_size(map_size):
    print("MapSize:")
    print("rows:", map_size.rows)
    print("cols:", map_size.cols)


def print_player(player):
    print("Player:")
    print("id:", player.id)
    print("currentPosition:")
    print_position(player.currentPosition)
    print("spawnBegin:")
    print_position(player.spawnBegin)
    print("score:", player.score)
    print("lives:", player.lives)
    print("speed:", player.speed)
    print("power:", player.power)
    print("delay:", player.delay)
    print("dragonEggSpeed:", player.dragonEggSpeed)
    print("dragonEggAttack:", player.dragonEggAttack)
    print("dragonEggDelay:", player.dragonEggDelay)
    print("dragonEggMystic:", player.dragonEggMystic)
    print("dragonEggMysticMinusEgg:", player.dragonEggMysticMinusEgg)
    print("dragonEggMysticAddEgg:", player.dragonEggMysticAddEgg)
    print("dragonEggMysticIsolateGate:", player.dragonEggMysticIsolateGate)
    print("box:", player.box)
    print("quarantine:", player.quarantine)
    print("gstEggBeingAttacked:", player.gstEggBeingAttacked)


def print_position(position):
    print("Position:")
    print("row:", position.row)
    print("col:", position.col)


def print_bomb(bomb):
    print("Bomb:")
    print("row:", bomb.row)
    print("col:", bomb.col)
    print("remainTime:", bomb.remainTime)
    print("playerId:", bomb.playerId)


def print_spoil(spoil):
    print("Spoil:")
    print("row:", spoil.row)
    print("col:", spoil.col)
    print("spoil_type:", spoil.spoil_type)


def print_dragon_egg_gst(dragon_egg_gst):
    print("DragonEggGST:")
    print("row:", dragon_egg_gst.row)
    print("col:", dragon_egg_gst.col)
    print("id:", dragon_egg_gst.id)


if __name__ == '__main__':
    map_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 5, 2, 2, 1, 2, 2, 2, 2, 0, 2, 2, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 0, 2, 2, 1],
        [1, 2, 2, 0, 2, 1, 2, 2, 2, 2, 0, 2, 2, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    map_data2 = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 3, 0, 2, 1],
        [1, 2, 5, 2, 2, 1, 2, 2, 2, 2, 0, 3, 0, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 0, 2, 3, 1],
        [1, 2, 2, 0, 2, 1, 2, 2, 2, 2, 0, 2, 2, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Test the A* search/ Dijkstra search with start and end points
    print(f"test search")
    dijkstra_path = dijkstra_search(map_data, (6, 5), (10, 2), [TerrainType.ROAD.value])
    astar_path = a_star_search(map_data, (6, 5), (10, 2), [TerrainType.ROAD.value])
    print(f"dijkstra_search {dijkstra_path}")
    print(f"a-star search {astar_path}")

    print("-----------------")
    print(f"test bomb")
    toggle_path = find_path_toggle_bomb(map_data, (10, 5), 4, [TerrainType.ROAD.value])
    print(f"toggle path {toggle_path}")

    print("-----------------")
    print(f"test finding best spoil")
    best_spoil = find_path_best_spoil(map_data, (5, 5), [(6, 1), (1, 1), (8, 2)],
                                      [TerrainType.ROAD.value, TerrainType.BALK.value])
    best_spoil_2 = find_path_best_spoil(map_data2, (10, 4), [(12, 1)],
                                        [TerrainType.ROAD.value, TerrainType.BALK.value])

    print(f"best_spoil path {best_spoil}")
    print(f"best_spoil2 path {best_spoil_2}")

    print("-----------------")
    print(f"test convert step")
    coordinates = [(5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (10, 4), (10, 3), (10, 2), (9, 2), (8, 2)]
    directions = coordinates_to_directions(coordinates)
    print(f"direction {directions}")

    print("-----------------")
    with open("../data/map.json", "r") as f:
        # Load the JSON data
        data = json.load(f)
    game_state = GameState(data)
    # print_game_state(game_state)
