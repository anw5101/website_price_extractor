import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright

# List of websites and corresponding XPaths
websites = [
# Gas Prices (87 unleaded; Waukee, IA) 
    {
        "url": "https://www.kwiktrip.com/locator/store?id=1056",
        "xpaths": {
            "Product Name": '//*[@id="storeInfoApp"]/div/div[2]/div[1]/div[2]/div[1]/div[1]',
            "Price": '//*[@id="storeInfoApp"]/div/div[2]/div[1]/div[2]/div[1]/div[3]/span[2]'
        }
    },
# Hy-Vee Skim Milk 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/2869496/Thats-Smart-Fat-Free-Skim-Milk",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '/html/body/div[1]/div/main/div/div/div/div[2]/div[2]/p[1]'
        }
    },
# Roma Tomatoes 
       {
        "url": "https://www.walmart.com/ip/Fresh-Roma-Tomato-Each/44390944",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
]

# Function to scrape Walmart using Playwright
def scrape_walmart():
    data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True to run in the background
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        
        page = context.new_page()

        for site in websites:
            url = site["url"]
            print(f"\n🔵 Opening: {url}")
            page.goto(url, timeout=60000)

            # Simulate human-like behavior
            time.sleep(random.uniform(3, 6))  # Random delay before extracting data
            page.mouse.wheel(0, random.randint(300, 700))  # Scroll down

            site_data = {"URL": url}

            for label, xpath in site["xpaths"].items():
                try:
                    element = page.locator(f'xpath={xpath}')
                    site_data[label] = element.text_content().strip()
                except Exception as e:
                    site_data[label] = "Not found"

            # Print extracted data for debugging
            print("✅ Extracted Data:", site_data)
            data.append(site_data)

            # Random delay between requests
            delay_time = random.randint(5, 15)
            print(f"⏳ Waiting {delay_time} seconds before next request...")
            time.sleep(delay_time)

        browser.close()

    # Save to Excel
    df = pd.DataFrame(data)
    df.to_excel("price_extractor_playwright.xlsx", index=False)
    print("\n🎉 Extraction complete! Data saved to price_extractor_playwright.xlsx")

# Run the scraper
scrape_walmart()
