"""
    browser.py
"""
from splinter import Browser
from selenium.webdriver.chrome.options import Options
from config import plog, CFConfig as cf, CFGameMode
from pygame.time import delay


class GameBrowser:
    browser: Browser = None

    def __init__(self, driver: str = 'chrome', maximize: bool = False, wsize: tuple = (1400, 900)) -> None:
        if maximize:
            self.browser = Browser(self.driver, fullscreen=maximize)
        else:
            chrome_options = Options()
            chrome_options.add_argument(f'--window-size={wsize[0]},{wsize[1]}')
            self.browser = Browser(self.driver, options=chrome_options)
        plog(self.browser)

    def get_game_id(self, secs: float = 1):
        if cf.Game.MODE == CFGameMode.MODE_TRAINING:
            training = self.browser.links.find_by_href(cf.Server.HREF_TRAINING)
            plog(training['href'])
            training.click()
            delay(secs)
            keybox = self.browser.find_by_name('teamkey')
            plog(keybox['placeholder'])
            keybox.click()
            delay(secs)
            keybox.type(cf.Server.DEMO_KEY)
            delay(secs)
            join_button = self.browser.find_by_text('Join Game')
            join_button.click()
            delay(secs)
            #
            self.gameid = self.browser.find_by_id('gameid').text
            plog(f'game_id {self.gameid}')
            delay(secs)
        elif cf.Game.MODE == CFGameMode.MODE_FIGHTING:
            fighting = self.browser.links.find_by_href(cf.Server.HREF_FIGHTING)
            plog(fighting['href'])
            fighting.click()
            delay(secs)
            # TODO ------------------------------------------------------
            gameid_str = 'xxx-yyy'
        return gameid_str

    def visit(self, url: str):
        plog(url)
        self.browser.visit(url)

    def quit(self):
        self.browser.quit()


if __name__ == '__main__':
    try:
        gameb = GameBrowser(maximize = True)
        gameb.visit(cf.Server.URL)
        gameb.get_game_id()
        while True:
            delay(3)
    except Exception:
        gameb.quit()
