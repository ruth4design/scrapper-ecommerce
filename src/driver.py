import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver(options: Options = None, disable_image=True, disable_js=False):
    # options = Options()
    if options is None:
        options = Options()
    else:
        options = options
    options.add_argument('--headless=new')
    # prefs = {
    #     "profile.managed_default_content_settings.images": 2,
        
    # }
    prefs = {}
    if disable_image:
        prefs["profile.managed_default_content_settings.images"] = 2
    if disable_js:
        prefs["profile.managed_default_content_settings.javascript"] = 2
    options.add_experimental_option("prefs", prefs)
    # use agent to avoid bot detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    #

    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

class Selector:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get(self, selector):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException as e:
            # print(f"An element was not found: {e}")
            return None
    def get_all(self, selector):
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, selector)
        except NoSuchElementException as e:
            # print(f"An element was not found: {e}")
            return None


def simulate_scroll(driver, timeout=3, logger=False):
    old_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        try:
            # Wait for the page to load more items, timeout after 'timeout' seconds.
            WebDriverWait(driver, timeout).until(
                lambda d, old_height=old_height: d.execute_script("return document.body.scrollHeight") > old_height
            )
            new_height = driver.execute_script("return document.body.scrollHeight")
            if logger:
                print(f"old_height: {old_height}, new_height: {new_height}")
            if new_height == old_height:
                break
            old_height = new_height
        except TimeoutException:
            # If no new content is loaded within the timeout, assume end of the page is reached
            break
    return driver
