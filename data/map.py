from enum import Enum


class TerrainType(Enum):
    ROAD = 0
    WALL = 1
    BALK = 2
    TELEPORT_GATE = 3
    QUARANTINE_PLACE = 4
    GST_DRAGON_EDGE = 5
    ROAD_WITH_BOMB = 6
    ROAD_WITH_EGG = 7
    ROAD_WITH_PLAYER = 8


class SpoilType(Enum):
    SPEED_EGG = 3
    ATTACH_EGG = 4
    DELAY_EGG = 5
    MYSTICS = 6


class Direction(Enum):
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    DOWN = (0, 1)
    UP = (0, -1)