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
import schedule
import os
import random
from datetime import datetime

# Location (Modify for your needs)
latitude = 41.616788  # Waukee, IA
longitude = -93.854709  # Waukee, IA
accuracy = 100  # Meters

# Load websites from Excel file
def load_websites(filename="websites.xlsx"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return []
    
    df = pd.read_excel(filename)
    
    websites = []
    for _, row in df.iterrows():
        if pd.isna(row["URL"]) or pd.isna(row["Product Name XPath"]) or pd.isna(row["Price XPath"]):
            continue  # Skip rows with missing data
        
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
    options.add_argument("--headless")  # Run in headless mode

    # Use a normal user-agent for better evasion
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Apply Selenium Stealth (MUST BE AFTER DRIVER INITIALIZATION)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver

# Main scraper function
def main_scraper_function():
    print("Loading websites from Excel file...")
    websites = load_websites()
    
    if not websites:
        print("No valid websites found in the Excel file.")
        return
    
    print("Starting web scraping...")

    # Store extracted data
    data = []

    for site in websites:
        url = site["url"]
        print(f"Opening: {url}")

        driver = initialize_driver()
        driver.get(url)

        site_data = {"URL": url}

        print(f"Waiting for 2 seconds for page to load...")
        time.sleep(2)

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
        print(f"Waiting {delay_time} seconds before the next request...")
        time.sleep(delay_time)

    # Save results to Excel
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

# Function to run scraper
def run_scraper():
    print("Running scraper at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    main_scraper_function()

# Schedule the scraper to run daily at 3 AM
schedule.every().day.at("15:43").do(run_scraper)

# Keep the script running to check and execute scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
