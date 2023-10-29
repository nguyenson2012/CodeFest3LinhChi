import heapq
import time

from core.tools.time_counter import measure_time


def get_neighbors(position):
    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    x, y = position
    return [(x + dx, y + dy) for dx, dy in offsets]


def is_valid_move(dimension_map_data, position, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road
    x, y = position
    return 0 <= x < len(dimension_map_data[0]) and 0 <= y < len(dimension_map_data) and dimension_map_data[y][
        x] in traversable_points


@measure_time
def dijkstra_search(dimension_map_data, start, end, traversable_points=None):
    if traversable_points is None:
        traversable_points = [0]  # road

    open_list = []
    closed_list = set()
    parents = {}

    # Add the start node to the open list
    heapq.heappush(open_list, (0, start))

    # Create a dictionary to keep track of g_costs
    g_costs = {start: 0}

    while open_list:

        # Get the node with the lowest g_cost
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

            if neighbor not in g_costs or tentative_g < g_costs[neighbor]:
                # Update the g_cost and parent node
                g_costs[neighbor] = tentative_g
                parents[neighbor] = current_node

                heapq.heappush(open_list, (tentative_g, neighbor))
    return None  # No path found
