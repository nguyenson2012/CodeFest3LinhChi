import heapq
import time

from core.tools.time_counter import measure_time


def heuristic(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])


def is_valid_move(dimension_map_data, position, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road
    x, y = position
    return 0 <= x < len(dimension_map_data[0]) and 0 <= y < len(dimension_map_data) and dimension_map_data[y][
        x] in traversable_points


def get_neighbors(position):
    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    x, y = position
    return [(x + dx, y + dy) for dx, dy in offsets]


@measure_time
def a_star_search(dimension_map_data, start, end, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road
    open_list = []
    closed_list = set()
    # Create a priority queue (heap) for open nodes, with the start node
    heapq.heappush(open_list, (0, start))
    # Create dictionaries to keep track of costs and parent nodes
    g_costs = {start: 0}
    f_costs = {start: heuristic(start, end)}
    parents = {}
    while open_list:
        # Get the node with the lowest f_cost
        current_cost, current_node = heapq.heappop(open_list)
        # Check if we've reached the end
        if current_node == end:
            find_path = []
            while current_node in parents:
                find_path.append(current_node)
                current_node = parents[current_node]
            return find_path[::-1]  # Return the path in reverse order

        closed_list.add(current_node)

        for neighbor in get_neighbors(current_node):
            if neighbor in closed_list or not is_valid_move(dimension_map_data, neighbor, traversable_points):
                continue
            # Calculate the tentative g_cost
            tentative_g = g_costs[current_node] + 1
            if neighbor not in [node for _, node in open_list] or tentative_g < g_costs[neighbor]:
                # Update the parent and g_cost
                parents[neighbor] = current_node
                g_costs[neighbor] = tentative_g
                f_costs[neighbor] = tentative_g + heuristic(neighbor, end)
                heapq.heappush(open_list, (f_costs[neighbor], neighbor))
    return None  # No path found
