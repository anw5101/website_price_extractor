from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import random
from datetime import datetime

# Read URLs and XPaths from Excel file
def load_xpaths_from_excel(filename="websites.xlsx"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []
    
    df = pd.read_excel(filename)
    websites = []
    
    for _, row in df.iterrows():
        websites.append({
            "url": row["URL"],
            "xpaths": {
                "Product Name": row["Product Name XPath"],
                "Price": row["Price XPath"]
            }
        })
    
    return websites

# Function to initialize the WebDriver
def initialize_driver():
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
    options.add_argument("--headless")  # Comment out this line to disable headless mode

    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32",
            webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
    return driver

# Define the main scraper function
def main_scraper_function():
    print("Scraping websites...")
    websites = load_xpaths_from_excel()
    if not websites:
        print("No URLs found. Exiting...")
        return

    data = []
    for site in websites:
        url = site["url"]
        print(f"Opening: {url}")
        
        driver = initialize_driver()
        driver.get(url)
        time.sleep(2)

        site_data = {"URL": url}
        for label, xpath in site["xpaths"].items():
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                site_data[label] = element.text.strip()
            except Exception:
                site_data[label] = "Not found"

        print(site_data)
        data.append(site_data)
        driver.quit()

        delay_time = random.randint(1, 5)
        print(f"Waiting {delay_time} seconds before next request...")
        time.sleep(delay_time)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = "price_extractor.xlsx"

    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        new_df = pd.DataFrame(data)
        merged_df = existing_df.merge(new_df, on="URL", how="left", suffixes=("", f"_{timestamp}"))
        merged_df.to_excel(filename, index=False)
    else:
        pd.DataFrame(data).to_excel(filename, index=False)

    print(f"Extraction complete! Data saved to {filename}.")

# Function to run the scraper
def run_scraper():
    print("Running scraper at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    main_scraper_function()

# Run the scraper immediately
run_scraper()
