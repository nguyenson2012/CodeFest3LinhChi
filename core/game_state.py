class GameState:
    def __init__(self, data):
        self.id = data.get("id")
        self.timestamp = data.get("timestamp")
        self.map_info = MapInfo(data.get("map_info"))
        self.tag = data.get("tag")
        self.player_id = data.get("player_id")
        self.gameRemainTime = data.get("gameRemainTime")


class MapInfo:
    def __init__(self, data):
        self.size = MapSize(data.get("size"))
        self.players = [Player(player_data) for player_data in data.get("players")]
        self.map = data.get("map")
        self.bombs = [Bomb(bomb_data) for bomb_data in data.get("bombs")]
        self.spoils = [Spoil(spoil_data) for spoil_data in data.get("spoils")]
        self.gameStatus = data.get("gameStatus")
        self.dragonEggGSTArray = [DragonEggGST(egg_data) for egg_data in data.get("dragonEggGSTArray")]


class MapSize:
    def __init__(self, data):
        self.rows = data.get("rows")
        self.cols = data.get("cols")


class Player:
    def __init__(self, data):
        self.id = data.get("id")
        self.currentPosition = Position(data.get("currentPosition"))
        self.spawnBegin = Position(data.get("spawnBegin"))
        self.score = data.get("score")
        self.lives = data.get("lives")
        self.speed = data.get("speed")
        self.power = data.get("power")
        self.delay = data.get("delay")
        self.dragonEggSpeed = data.get("dragonEggSpeed")
        self.dragonEggAttack = data.get("dragonEggAttack")
        self.dragonEggDelay = data.get("dragonEggDelay")
        self.dragonEggMystic = data.get("dragonEggMystic")
        self.dragonEggMysticMinusEgg = data.get("dragonEggMysticMinusEgg")
        self.dragonEggMysticAddEgg = data.get("dragonEggMysticAddEgg")
        self.dragonEggMysticIsolateGate = data.get("dragonEggMysticIsolateGate")
        self.box = data.get("box")
        self.quarantine = data.get("quarantine")
        self.gstEggBeingAttacked = data.get("gstEggBeingAttacked")


class Position:
    def __init__(self, data):
        self.row = data.get("row")
        self.col = data.get("col")


class Bomb:
    def __init__(self, data):
        self.row = data.get("row")
        self.col = data.get("col")
        self.remainTime = data.get("remainTime")
        self.playerId = data.get("playerId")


class Spoil:
    def __init__(self, data):
        self.row = data.get("row")
        self.col = data.get("col")
        self.spoil_type = data.get("spoil_type")


class DragonEggGST:
    def __init__(self, data):
        self.row = data.get("row")
        self.col = data.get("col")
        self.id = data.get("id")
