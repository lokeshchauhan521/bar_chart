import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
import time
import logging
import pickle

# Configure logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='scraper.log',  # Log to file
                    filemode='a')

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Function to create Selenium driver
def create_driver():
    try:
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = uc.Chrome(options=options)
        logging.info("\u2705 Driver created successfully")
        return driver
    except WebDriverException as e:
        logging.error(f"\ud83d\udeab Error creating driver: {e}")

# Function to save and load cookies
def save_cookies(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, path):
    try:
        with open(path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        logging.warning("\u26a0\ufe0f No cookies found.")

# Function to wait for full page load
def wait_for_full_page_load(driver, timeout=30):
    try:
        time.sleep(30)  # Wait for 30 seconds explicitly
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        logging.info("\u2705 Page fully loaded.")
    except TimeoutException:
        logging.warning("\u23f3 Page load timeout reached.")

# Function to scroll to bottom
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    logging.info("\u2705 Scrolled to bottom.")

# Function to download entire HTML and save
def download_full_html(driver):
    try:
        logging.info("\u23f3 Waiting for page to load...")
        wait_for_full_page_load(driver)
        scroll_to_bottom(driver)
        full_page_html = driver.page_source
        with open('full_page.html', 'w', encoding='utf-8') as file:
            file.write(full_page_html)
        logging.info("\u2705 Full page HTML saved successfully.")
    except WebDriverException as e:
        logging.error(f"\ud83d\udeab WebDriverException: {e}")
    except Exception as e:
        logging.warning(f"\u26a0\ufe0f Unexpected Error: {e}")

# Function to find element by ID
def find_element_by_id(driver, element_id):
    try:
        logging.info("\u23f3 Searching for element by ID...")
        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        logging.info(f"\u2705 Element with ID '{element_id}' found.")
        return element
    except TimeoutException:
        logging.error(f"\u23f0 Timeout Error: Element with ID '{element_id}' not found.")
    except WebDriverException as e:
        logging.error(f"\ud83d\udeab WebDriverException: {e}")
    except Exception as e:
        logging.warning(f"\u26a0\ufe0f Unexpected Error: {e}")

# Function to handle session expired
def handle_session_expired(driver):
    try:
        refresh_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Refresh') or contains(text(),'reload')]")
        ))
        refresh_button.click()
        logging.info("\u2705 Session expired. Refresh clicked.")
    except TimeoutException:
        logging.info("\u23f0 No session expired popup found.")

# Execution steps
url = 'https://www.barchart.com/futures'
cookies_path = 'cookies.pkl'

driver = create_driver()
if driver:
    try:
        driver.get(url)
        wait_for_full_page_load(driver)
        load_cookies(driver, cookies_path)
        driver.refresh()
        download_full_html(driver)
        element = find_element_by_id(driver, '_root')

        if element is None:
            handle_session_expired(driver)
            time.sleep(5)
            download_full_html(driver)

        save_cookies(driver, cookies_path)
    finally:
        driver.quit()
        logging.info("\ud83d\udcaa Driver closed.")
else:
    logging.warning("\u26a0\ufe0f Failed to create WebDriver.")
