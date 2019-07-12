from streaming.scraper.api.snapshot import Snapshot
from streaming.config import config
from selenium import webdriver

class Screenshot():
    def __init__(self, url, grid=config['selenium']['hub'], browser='chrome'):
        self.url = url
        self.grid = grid
        self.browser = browser

    def to_png(self):
        driver = webdriver.Remote( command_executor=self.grid,
                desired_capabilities={ "browserName": self.browser })
        try:
            print("Screenshot for {0}".format(self.url))
            driver.get(self.url)
            screenshot_data = driver.get_screenshot_as_png()
            driver.quit()
            Snapshot(self.url).create(screenshot_data)

        except Exception as err:
            print(err)
            driver.quit()
            pass
