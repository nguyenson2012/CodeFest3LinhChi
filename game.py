"""
    game.py
"""
from config.config import CFConfig as cf, plog
from browser import GameBrowser
from connection.sioclient import CFSocket
import pygame as pg
from sys import argv
from data.strat_dummy import get_next_move

"""
=================================DEMO=========================================
"""

class Player:
    """
        Player object run
    """
    client: CFSocket = None

    def __init__(self, gameid: str, playerid: str) -> None:
        self.client = CFSocket(gameid, playerid)

    def connect_and_join(self):
        self.client.sio_connect()
        retry: int = 0
        while retry < 10:
            pg.time.wait(200)
            if self.client.is_connected():
                self.client.join_game()
                break
            retry += 1

    def quite_game(self):
        self.client.sio_terminate()


# ==========================================================================
#                           GamePlay AI
#   Add or replace the Dummy AI here
# ==========================================================================

    def move_player(self, gamewindow: pg.Surface = None):
        """
            Calling AI from here
        """
        if self.client.is_startgame:
            # Don't move by default
            next_move = cf.MoveSet.STOP
            ############################### Dummy AI
            next_move = get_next_move(self.client.map_json)
            ###############################
            self.client.direct_player(next_move)
            if gamewindow != None:
                gamewindow.blit(pg.font.SysFont('Monaco',72).render(next_move,True,(255,128,0)), (40, 40))


# ==========================================================================
#                           Main Loop
# ==========================================================================

def main_loop(player: Player, winflags: int = 0):
    pg.init()
    clock = pg.time.Clock()
    GameMain = pg.display.set_mode((cf.Game.W_WIDTH, cf.Game.W_HEIGHT), flags=winflags)
    pg.display.set_caption(f'{cf.Game.TITLE} - {player.client.player_id}')
    GameMain.fill((255,255,255))

    running = True
    while running:
        # For shown window
        for event in pg.event.get():
            # Check for QUIT event. If QUIT, then set running to false.
            if event.type == pg.QUIT:
                running = False
                plog(event)
        # For hidden window
        if player.client.is_stoptraining:
            running = False

        # Clear screen
        GameMain.fill((0, 0, 0))

        # Decide the next move
        player.move_player(GameMain)

        # Update the display
        pg.display.flip()

        # Program frames per second
        clock.tick(5) # ~200ms/move
    #
    player.quite_game()
    pg.quit()


def main_player():
    gameb = GameBrowser()
    gameb.visit(cf.Server.URL)
    game_room = gameb.get_game_id()
    player = Player(game_room, cf.Server.PLAYER_1_ID)
    player.connect_and_join()
    main_loop(player)
    gameb.quit()

def buddy_player():
    game_room = input('Game ID: ')
    player = Player(game_room, cf.Server.PLAYER_2_ID)
    player.connect_and_join()
    main_loop(player, pg.HIDDEN)


if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == 'buddy':
        buddy_player()
    else:
        main_player()
