"""
    game.py
"""
from config.config import CFConfig as cf, plog
from connection.sioclient import CFSocket
import pygame as pg
from sys import argv
from strategy.strat_dummy import get_next_move, get_next_move_random


def move_player(player: CFSocket, strat: int):
    """
        Calling AI from here
    """
    if player.is_startgame or player.is_midgame:
        # Don't move by default
        next_move = cf.MoveSet.STOP

        # ===========================================================
        # Add or replace the Dummy AI here
        if strat == 1:
            next_move = get_next_move(player.player_id, player.map_json)
        elif strat == 2:
            next_move = get_next_move_random()
        # ===========================================================

        player.direct_player(next_move)
        #
        player = [x for x in player.map_json['map_info']['players'] if x['id'] == player.player_id][0]
        return player['lives']
    else:
        return None


# ==========================================================================
#                           Main Loop
# ==========================================================================

def main_loop(game_id: str, player_id: str, strat: int = 1):
    pg.init()
    clock = pg.time.Clock()
    GameMain = pg.display.set_mode((cf.Game.W_WIDTH, cf.Game.W_HEIGHT))

    player = CFSocket(game_id, player_id)
    player.connect_and_join()

    pg.display.set_caption(f'{cf.Game.TITLE} - {player.player_id}')
    pg.display.set_icon(pg.image.load('./data/3TinElephants_1024.jpg'))
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
        if player.is_stoptraining:
            running = False

        # Clear screen
        GameMain.fill((0, 0, 0))

        # Decide the next move
        lives = move_player(player, strat)
        if lives != None:
            GameMain.blit(pg.font.SysFont('Monaco',72).render(str(lives),True,(255,128,0)), (40, 40))

        # Update the display
        pg.display.flip()

        # Program frames per second
        clock.tick(5) # ~200ms/move
    #
    player.quite_game()
    pg.quit()


if __name__ == '__main__':
    assert len(argv) >= 3, 'Need to provide both game_id and player_id'
    if len(argv) == 4:
        main_loop(argv[1], argv[2], argv[3])
    else:
        main_loop(argv[1], argv[2])
