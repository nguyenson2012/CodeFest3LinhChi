import time

import heapq

from core.tools.time_counter import measure_time


def is_valid_move(dimension_map_data, position, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road
    x, y = position
    return 0 <= x < len(dimension_map_data[0]) and 0 <= y < len(dimension_map_data) and dimension_map_data[y][
        x] in traversable_points


def find_best_path(map_data, start, end, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road
    x_end, y_end = end

    priority_queue = [(0, start)]
    visited = set()
    parents = {}
    while priority_queue:
        priority, (x, y) = heapq.heappop(priority_queue)

        if (x, y) == (x_end, y_end):
            path = []
            current = (x_end, y_end)
            while current:
                path.append(current)
                current = parents.get(current)
            path.reverse()
            return path

        if (x, y) in visited:
            continue

        visited.add((x, y))

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if is_valid_move(map_data, (new_x, new_y), traversable_points):
                if (new_x, new_y) in visited:
                    continue

                if map_data[new_y][new_x] == 0:  # road
                    new_priority = priority
                elif map_data[new_y][new_x] == 2:  # balk
                    new_priority = priority + 1
                else:
                    new_priority = priority + 10

                heapq.heappush(priority_queue, (new_priority, (new_x, new_y)))
                parents[(new_x, new_y)] = (x, y)
    return None


# Public to use
@measure_time
def find_path_best_spoil(map_data, start_position, spoil_locations, traversable_points=None):
    best_path = None
    min_balk_count = float('inf')

    for x, y in spoil_locations:
        # use custom a star
        path = find_best_path(map_data, start_position, (x, y), traversable_points)
        print(path)
        if path is not None:
            balk_count = sum(1 for x, y in path if map_data[y][x] == 2)  # 2 is balk
            if balk_count < min_balk_count:
                best_path = path
                min_balk_count = balk_count

    return best_path
