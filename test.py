import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import random
import time
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Function to create Selenium driver
def create_driver(path):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # options.add_argument('--headless=new')
        driver = webdriver.Chrome(options=options)
        print("Driver created successfully")
        return driver
    except Exception as e:
        print(f"Error creating driver: {e}")

# Function to download HTML
def download_page(url, driver_path):
    driver = create_driver(driver_path)
    try:
        driver.get(url)
        time.sleep(10) 
        html = driver.page_source
        with open("futures_market.html", "w", encoding="utf-8") as file:
            file.write(html)
        print("Page downloaded successfully")
    except Exception as e:
        print(f"Error downloading page: {e}")
    finally:
        if driver:
            driver.quit()

# Function to extract data from HTML
def extract_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Locate the table
    table = soup.find("table", {"class": "bc-table-scrollable"})
    data = []
    headers = [header.text for header in table.find_all("th")]

    for row in table.find_all("tr", class_="bc-table-row"):
        cols = row.find_all("td")
        if cols:
            data.append([col.text.strip().replace(',', '') for col in cols])

    df = pd.DataFrame(data, columns=headers)
    return df

# Data analysis function
def perform_analysis(df):
    # Convert columns to numeric where necessary
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Change'] = pd.to_numeric(df['Change'], errors='coerce')

    # Create 'Mean' column
    df['Mean'] = (df['High'] + df['Low']) / 2

    # Plot the data
    plt.figure(figsize=(14, 6))
    plt.plot(df['High'], label='High', color='blue')
    plt.plot(df['Low'], label='Low', color='red')
    plt.plot(df['Mean'], label='Mean', color='green', linestyle='--')
    plt.title('High, Low and Mean of Futures Market')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    plt.show()

    # Find row with largest 'Change'
    max_change_row = df.loc[df['Change'].idxmax()]
    print(f"Contract with largest change: {max_change_row['Contract Name']}")
    print(f"Last: {max_change_row['Last']}")

    # Save to Excel
    with pd.ExcelWriter('futures_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)

# Execution steps
driver_path = '/path/to/chromedriver'  # Change to actual path
url = 'https://www.barchart.com/futures'

# Step 1: Download page
download_page(url, driver_path)

# Step 2: Extract and analyze data
df = extract_data('futures_market.html')
perform_analysis(df)
