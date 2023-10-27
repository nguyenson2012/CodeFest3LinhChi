def coordinates_to_directions(coordinates):
    directions = []
    prev_x, prev_y = coordinates[0]

    for x, y in coordinates[1:]:
        if x > prev_x:
            directions.append(2)  # Move RIGHT
        elif x < prev_x:
            directions.append(1)  # Move LEFT
        elif y > prev_y:
            directions.append(4)  # Move DOWN
        elif y < prev_y:
            directions.append(3)  # Move UP
        else:
            directions.append(0)  # Stop Moving

        prev_x, prev_y = x, y

    return directions
