"""
    game.py
"""
from config import CFConfig as cf, plog, CFGameMode
from browser import GameBrowser
from sioclient import CFSocket
from concurrent.futures import ThreadPoolExecutor
import keyboard
# for demo only
from time import sleep
from random import randint


"""
=================================DEMO=========================================
"""

class RandomPlay:
    """
        Random run
    """
    MOVE_SET = ['1','2','3','4','b','x']
    TOTAL_MOVES = 60
    player: CFSocket = None
    running: bool = False

    def __init__(self, gameid: str, playerid: str) -> None:
        self.player = CFSocket(gameid, playerid)

    def random_controller(self):
        plog('Random controller is called!')
        self.running = True
        for m in range(self.TOTAL_MOVES):
            sleep(2)
            plog(f'{self.player.player_id} step {m}')
            move = self.MOVE_SET[randint(0, len(self.MOVE_SET)-1)]
            self.player.direct_player(move)
            if not self.running:
                break

    def play_main(self):
        self.player.sio_connect()
        sleep(2)
        self.player.join_game()
        sleep(5)
        self.player.run_job(self.random_controller)
        self.player.sio_wait()

    def play_exit(self):
        self.player.sio_terminate()
        self.running = False


browser: GameBrowser = None
play_1: RandomPlay = None
play_2: RandomPlay = None

def start_game():
    global browser, play_1, play_2
    # must use the same gamebrowser to get the same game_id
    browser = GameBrowser()
    browser.visit(cf.Server.URL)
    gameid = browser.get_game_id(0.5)
    play_1 = RandomPlay(gameid, cf.Server.PLAYER_1_ID)
    play_2 = RandomPlay(gameid, cf.Server.PLAYER_2_ID)

    with ThreadPoolExecutor(3) as executor:
        for future in [
            executor.submit(play_1.play_main),
            executor.submit(play_2.play_main)
        ]:
            plog(future.result())

def end_game(key):
    plog(f'End Game Sent ---------- {key}')
    play_1.play_exit()
    play_2.play_exit()
    sleep(3)
    browser.quit()


if __name__ == '__main__':
    if cf.Game.MODE == CFGameMode.MODE_TRAINING:
        try:
            keyboard.on_press_key('z', end_game)
            start_game()
        except Exception as exc:
            plog(f'Exception coccured {exc}')