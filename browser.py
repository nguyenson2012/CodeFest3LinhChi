"""
    browser.py
"""
from splinter import Browser
from selenium.webdriver.chrome.options import Options
from config import plog, CFConfig as cf, CFGameMode
from time import sleep


class GameBrowser:
    driver: str = None
    browser: Browser = None

    def __init__(self, driver: str = 'chrome', maximize: bool = False, wsize: tuple = (1600, 900)) -> None:
        self.driver = driver
        if maximize:
            self.browser = Browser(self.driver, fullscreen=maximize)
        else:
            chrome_options = Options()
            chrome_options.add_argument(f'--window-size={wsize[0]},{wsize[1]}')
            self.browser = Browser(self.driver, options=chrome_options)
        plog(self.browser)

    def get_game_id(self, delay: float = 1):
        gameid_str = ''
        if cf.Game.MODE == CFGameMode.MODE_TRAINING:
            training = self.browser.links.find_by_href(cf.Server.HREF_TRAINING)
            plog(training['href'])
            training.click()
            sleep(delay)
            keybox = self.browser.find_by_name('teamkey')
            plog(keybox['placeholder'])
            keybox.click()
            sleep(delay)
            keybox.type(cf.Server.DEMO_KEY)
            sleep(delay)
            join_button = self.browser.find_by_text('Join Game')
            join_button.click()
            sleep(delay)
            gameid_str = self.browser.find_by_id('gameid').text
            plog(f'game_id {gameid_str}')
            sleep(delay)
        elif cf.Game.MODE == CFGameMode.MODE_FIGHTING:
            fighting = self.browser.links.find_by_href(cf.Server.HREF_FIGHTING)
            plog(fighting['href'])
            fighting.click()
            sleep(delay)
            # TODO ------------------------------------------------------
            gameid_str = 'xxx-yyy'
        return gameid_str

    def visit(self, url: str):
        plog(url)
        self.browser.visit(url)

    def quit(self):
        self.browser.quit()


if __name__ == '__main__':
    gameb = GameBrowser(maximize = True)
    gameb.visit(cf.Server.URL)
    gameb.get_game_id()
    gameb.quit()
