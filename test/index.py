# Example usage:
from core.algorithm.common.a_star_search import a_star_search
from core.algorithm.common.dijkstra_search import dijkstra_search
from core.algorithm.find_path_best_spoil import find_path_best_spoil
from core.algorithm.find_path_toggle_bomb import find_path_toggle_bomb
from core.tools.converter import coordinates_to_directions
from data.map import TerrainType

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
    coordinates = [(5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (10, 4), (10, 3), (10, 2), (9, 2), (8, 2)]
    directions = coordinates_to_directions(coordinates)
    print(f"best_spoil path {best_spoil}")
    print(f"direction {directions}")
