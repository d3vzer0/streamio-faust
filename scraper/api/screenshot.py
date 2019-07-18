from streaming.scraper.api.snapshot import Snapshot
from streaming.config import config
from selenium.common.exceptions import WebDriverException
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
            driver.close()
            driver.quit()
            Snapshot(self.url).create(screenshot_data)

        except WebDriverException as err:
            print(err)
            pass

        except Exception as err:
            print(err)
            driver.close()
            driver.quit()
            pass
