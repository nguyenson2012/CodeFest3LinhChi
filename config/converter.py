from config.config import CFConfig


def coordinates_to_directions(coordinates):
    directions = []
    prev_x, prev_y = coordinates[0]

    for x, y in coordinates[1:]:
        if x > prev_x:
            directions.append(CFConfig.MoveSet.RIGHT)  # Move RIGHT
        elif x < prev_x:
            directions.append(CFConfig.MoveSet.LEFT)  # Move LEFT
        elif y > prev_y:
            directions.append(CFConfig.MoveSet.DOWN)  # Move DOWN
        elif y < prev_y:
            directions.append(CFConfig.MoveSet.UP)  # Move UP
        else:
            directions.append(CFConfig.MoveSet.STOP)  # Stop Moving

        prev_x, prev_y = x, y

    return directions
