import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

@pytest.fixture(scope="module")
def driver():
    """
    Fixture to set up and tear down the WebDriver.
    
    Initializes ChromeDriver with mobile emulation options,
    clears cache and cookies before yielding the driver for use in tests.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    mobile_emulation = {
        "deviceMetrics": {"width": 775, "height": 1612, "pixelRatio": 3.0},
        "userAgent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) "
                      "AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 "
                      "Mobile/15A372 Safari/604.1")
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    driver = webdriver.Chrome(options=chrome_options)
    clear_cache(driver)
    yield driver
    driver.quit()

def clear_cache(driver):
    """
    Clears browser cache and cookies using Chrome DevTools Protocol (CDP).
    """
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    print("Cache and cookies cleared.")

def test_twitch_stream(driver):
    """
    Test to automate Twitch.tv to search for 'StarCraft II' streams and
    select a random stream to verify video playback.

    Steps:
    1. Open Twitch.tv and accept the cookie consent banner.
    2. Perform a search for 'StarCraft II'.
    3. Scroll down the page to load more streams.
    4. Select a random stream and handle any modal pop-ups.
    5. Verify that the stream video loads and take a screenshot.

    Expected Result:
    The script should successfully navigate to a random 'StarCraft II' stream,
    handle any modal pop-ups, and confirm that the video player is loaded.
    """
    driver.get('https://www.twitch.tv')
    wait = WebDriverWait(driver, 10)

    handle_cookie_consent(driver, wait)
    perform_search(driver, wait, 'StarCraft II')
    scroll_down_page(driver)
    select_random_stream(driver, wait)

def handle_cookie_consent(driver, wait):
    """
    Handles the cookie consent banner if it appears on the page.
    """
    try:
        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-a-target="consent-banner-accept"]')))
        accept_button.click()
        print("Accepted cookie consent banner.")
    except Exception:
        print("Cookie consent banner not found or could not be clicked.")

def perform_search(driver, wait, search_query):
    """
    Performs a search on Twitch.tv for the specified query.

    :param driver: WebDriver instance.
    :param wait: WebDriverWait instance.
    :param search_query: Query to search for.
    """
    search_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@aria-label="Search"]')))
    wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@aria-label="Search"]'))).click()

    search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-a-target="tw-input"]')))
    search_input.send_keys(search_query)
    search_input.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.XPATH, '//img[contains(@class, "tw-image")]')))

def scroll_down_page(driver):
    """
    Scrolls down the page twice to load more content.

    :param driver: WebDriver instance.
    """
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)

def select_random_stream(driver, wait):
    """
    Selects a random stream from the search results and verifies video playback.

    :param driver: WebDriver instance.
    :param wait: WebDriverWait instance.
    """
    streams = driver.find_elements(By.XPATH, '//img[contains(@class, "tw-image")]')

    if streams:
        random_stream = random.choice(streams)
        driver.execute_script("arguments[0].scrollIntoView(true);", random_stream)
        
        wait.until(EC.visibility_of(random_stream))
        wait.until(EC.element_to_be_clickable(random_stream))
        
        driver.execute_script("arguments[0].click();", random_stream)
        
        handle_modal_popups(driver, wait)
        
        wait.until(EC.presence_of_element_located((By.XPATH, '//video')))
        driver.save_screenshot('screenshot.png')
    else:
        print("No streams found for 'StarCraft II'.")

def handle_modal_popups(driver, wait):
    """
    Handles any modal pop-ups that might appear before the video loads.

    :param driver: WebDriver instance.
    :param wait: WebDriverWait instance.
    """
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]')))
        close_button.click()
        print("Closed modal pop-up.")
    except Exception:
        print("No modal pop-up found.")

if __name__ == "__main__":
    pytest.main(["-v"])
