import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
import time

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Function to create Selenium driver
def create_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        print("✅ Driver created successfully")
        return driver
    except WebDriverException as e:
        print(f"🚫 Error creating driver: {e}")

# Function to download entire HTML and save
def download_full_html(driver):
    try:
        # Wait until the element with id='_root' is present
        print("⏳ Waiting for page to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "_root"))
        )
        time.sleep(random.randint(5, 10))  # Random delay to avoid bot detection
        full_page_html = driver.page_source
        with open('full_page.html', 'w', encoding='utf-8') as file:
            file.write(full_page_html)
        print("✅ Full page HTML saved successfully.")
    except TimeoutException:
        print("⏰ Timeout Error: '_root' element not found.")
    except WebDriverException as e:
        print(f"🚫 WebDriverException: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")

# Execution steps
url = 'https://www.barchart.com/futures'

driver = create_driver()
if driver:
    try:
        driver.get(url)
        download_full_html(driver)
    finally:
        driver.quit()
        print("🚪 Driver closed.")
else:
    print("⚠️ Failed to create WebDriver.")
