from core.algorithm.common.a_star_search import a_star_search
from core.tools.time_counter import measure_time


# Public to use
@measure_time
def find_path_toggle_bomb(map_data, bomb_position, bomb_size, traversable_points=None):
    x, y = bomb_position

    # Detect which cells effected by bomb
    affected_cells = []
    for i in range(1, bomb_size + 1):
        if y + i < len(map_data):
            affected_cells.append((x, y + i))
        if y - i >= 0:
            affected_cells.append((x, y - i))
        if x + i < len(map_data[0]):
            affected_cells.append((x + i, y))
        if x - i >= 0:
            affected_cells.append((x - i, y))

    # List of cells are road
    road_cells = [(x, y) for x in range(len(map_data[0])) for y in range(len(map_data)) if
                  map_data[y][x] == 0]

    # Remove dangerous cells
    safe_cells = [cell for cell in road_cells if cell not in affected_cells]

    # Use a star algorithm to find a short path to a point
    start = bomb_position  # Position of player after planing bomb
    shortest_path = None
    shortest_path_length = float('inf')

    for cell in safe_cells:
        path = a_star_search(map_data, start, cell, traversable_points)
        if path and len(path) < shortest_path_length:
            shortest_path = path
            shortest_path_length = len(path)

    return shortest_path
