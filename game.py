"""
    game.py
"""
from config.config import CFConfig as cf, plog
from connection.sioclient import CFSocket
import tkinter as tk
from sys import argv
from strategy.strat_dummy import get_next_move


def move_player(client: CFSocket):
    """
        Calling AI from here
    """
    if client.is_startgame or client.is_midgame:
        # Don't move by default
        next_move = cf.MoveSet.STOP

        # ===========================================================
        # Add or replace the Dummy AI here
        next_move = get_next_move(client)
        # ===========================================================

        client.direct_player(next_move)
        #
        return client.player.lives
    else:
        return None


# ==========================================================================
#                           Main Loop
# ==========================================================================

def main_loop(game_id: str = None, player_id: str = None):
    root = tk.Tk()

    if game_id == None or player_id == None:
        game_id, player_id = root.clipboard_get().split(' ')

    root.title(f'{cf.Game.TITLE} - {player_id}')
    root.iconbitmap(cf.Game.IMAGE)
    root.geometry(f'{cf.Game.W_WIDTH}x{cf.Game.W_HEIGHT}')

    image = tk.PhotoImage(file=cf.Game.IMAGE)
    label = tk.Label(root, text=cf.Game.TITLE, anchor=tk.NE, image=image, compound=tk.LEFT, font=('Monaco', 40), fg='Red')
    label.pack()

    client = CFSocket(game_id, player_id)
    client.connect_and_join()

    def update():
        # Decide the next move
        lives = move_player(client)
        if lives != None:
            label.config(text=str(lives))

        # quit game
        if client.is_stoptraining:
            root.destroy()

        # Schedule the next update after xxx milliseconds
        root.after(cf.Game.TIMEOUT, update)

    # will be called each xxx msec
    update()

    # Tk mainloop
    root.mainloop()

    # disconnect
    client.quite_game()


if __name__ == '__main__':
    if len(argv) == 3:
        main_loop(argv[1], argv[2])
    else:
        main_loop()
