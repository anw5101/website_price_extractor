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
        "url": "https://www.hy-vee.com/aisles-online/p/8657/Roma-Tomatoes",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
        }
    },
# Cap N Crunch Cereal 
        {
        "url": "https://www.hy-vee.com/aisles-online/p/3367762/Quaker-Capn-Crunch-Regular-Cereal",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
        }
    },
# Sara Lee Brioche Hamburger Buns
{
        "url": "https://www.hy-vee.com/aisles-online/p/3512698/Sara-Lee-Artesano-Brioche-Buns-8-count",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# GV Mayonnaise 
{
        "url": "https://www.hy-vee.com/aisles-online/p/2886456/Thats-Smart-Mayonnaise",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Canned Pears 
 {
        "url": "https://www.hy-vee.com/aisles-online/p/57770/HyVee-Light-Bartlett-Pear-Halves-In-Pear-Juice-From-Concentrate",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Romaine Lettuce Hearts 3x 
   {
        "url": "https://www.hy-vee.com/aisles-online/p/1882763/Dole-Fresh-Romaine-Hearts",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Oven Roasted Turkey Breast 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/23969/HyVee-Oven-Roasted-Cured-Turkey-Breast-And-White-Turkey-Shaved-Slices",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Cottage Cheese
    {
        "url": "https://www.hy-vee.com/aisles-online/p/2912532/Thats-Smart-Small-Curd-Cottage-Cheese-4-Milkfat",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Fairlife Skim Milk
    {
        "url": "https://www.hy-vee.com/aisles-online/p/1415790/Fairlife-Fat-Free-UltraFiltered-Milk",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Bananas 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/37178/Fresh-Chiquita-Bananas",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/div[1]/div[2]/span[1]"
        }
    },
# Clementines 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/371584/Wonderful-Halos-Mandarin-Oranges",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# 90/10 Ground Beef
    {
        "url": "https://www.hy-vee.com/aisles-online/p/31823/Certified-Ground-Round-90-Lean-10-Fat",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Boneless Chicken Breast 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/65791/Boneless-Skinless-Chicken-Breast",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Ram 1500 
   {
        "url": "https://www.ramtrucks.com/ram-1500.html",
        "xpaths": {
            "Product Name": "//*[@id='secondary_navigation']/div/div/div/div[1]/div[1]/div/div[1]/div/div[3]",
            "Price": "//*[@id='blurb_rail_copy_copy']/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div[2]"
        }
    },
# Chevrolet Silverado 1500 
    {
        "url": "https://www.chevrolet.com/trucks/silverado/1500",
        "xpaths": {
            "Product Name": "//*[@id='gb-main-content']/gb-adv-grid[4]/adv-col/div/gb-adv-grid/adv-col/div/gb-adv-grid/adv-col/div/div[1]/div/p/span",
            "Price": "//*[@id='gb-main-content']/gb-adv-grid[2]/adv-col[2]/div/gb-adv-grid/adv-col[1]/div/div/div/p/span"
        }
    },
# 2x4 8' Lumber 
    {
        "url": "https://www.menards.com/main/building-materials/lumber-boards/dimensional-lumber/2-x-4-construction-framing-lumber/1021101/p-1444451086852-c-13125.htm",
        "xpaths": {
            "Product Name": "//*[@id='itemDetails']/div/div[2]/div/div[1]/h1",
            "Price": "//*[@id='itemDetails']/div/div[2]/div/div[3]/div[2]/div/div[1]/span[2]"
        }
    },
# Maple Syrup 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/22365/HyVee-Select-100-Pure-Maple-Syrup",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Eggs 
    {
        "url": "https://www.hy-vee.com/aisles-online/p/2849570/Thats-Smart-Large-Shell-Eggs",
        "xpaths": {
            "Product Name": "//*[@id='main']/div/div/div[2]/div[2]/h1",
            "Price": "//*[@id='main']/div/div/div[2]/div[2]/p[1]"
        }
    },
# Samsung Washing Machine
    {
        "url": "https://www.homedepot.com/p/Samsung-5-5-cu-ft-Extra-Large-Capacity-Smart-Top-Load-Washer-with-Super-Speed-in-White-WA55CG7100AW/325807860",
        "xpaths": {
            "Product Name": "//*[@id='zone-a']/div/div/div[2]/div[1]/div[1]/div/div[3]/span/h1",
            "Price": "//*[@id='eco-rebate-price']/div/div[1]/div/div/span[2]"
        }
    },
# Samsung Dryer
   {
        "url": "https://www.homedepot.com/p/Samsung-7-4-cu-ft-Vented-Smart-Front-Load-Electric-Dryer-with-Steam-Sanitize-in-White-DVE55CG7100W/325807880",
        "xpaths": {
            "Product Name": "//*[@id='zone-a']/div/div/div[2]/div[1]/div[1]/div/div[3]/span/h1",
            "Price": "//*[@id='eco-rebate-price']/div/div[1]/div/div/span[2]"
        }
    },
    
    # The below lines can be used to copy/paste to add new products to the website query. 
    # {
    #     "url": "",
    #     "xpaths": {
    #         "Product Name": '',
    #         "Price": ''
    #     }
    # },
]

# Location (Modify for your needs)
latitude = 41.616788   # Waukee, IA
longitude = -93.854709 # Waukee, IA 
accuracy = 100         # Meters

# Function to initialize the WebDriver with proxy and options
def initialize_driver(proxy=None):
    options = Options()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')  # Set proxy server

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
    # options.add_argument("--headless")  # Comment out this line to disable headless mode

    # Use a normal user-agent for better evasion of bot detection
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

# Define the main scraper function
def main_scraper_function():
    print("Scraping websites...")
    # Store extracted data
    data = []

    for site in websites:
            url = site["url"]
            print(f"Opening: {url}")
            
            # Initialize a new driver for each website
            driver = initialize_driver()
            driver.get(url)

            site_data = {"URL": url}

            print(f"Waiting for {2} seconds for page to load...")
            time.sleep(2)
            print("Done waiting!")

            for label, xpath in site["xpaths"].items():
                try:
                    # Wait up to 20 seconds for the element to appear
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    site_data[label] = element.text.strip()
                except Exception as e:
                    site_data[label] = "Not found"

            # Print the extracted data for the current website
            print(site_data)

            data.append(site_data)

            # Close browser after extracting data for the current website
            driver.quit()

            # Add a randomized delay before the next request (helps avoid detection)
            delay_time = random.randint(1, 5)  # Delay between 1 to 5 seconds
            print(f"Waiting for {delay_time} seconds before the next request...")
            time.sleep(delay_time)

    # Generate timestamp for column name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Define filename
    filename = "price_extractor_draft.xlsx"

    # Check if the file already exists
    if os.path.exists(filename):
        # Load existing data
        existing_df = pd.read_excel(filename)
        
        # Align new data with previous entries
        new_df = pd.DataFrame(data)

        # Ensure data alignment by merging based on "URL"
        merged_df = existing_df.merge(new_df, on="URL", how="left", suffixes=("", f"_{timestamp}"))

        # Save updated dataframe back to the same file
        merged_df.to_excel(filename, index=False)
    else:
        # If file does not exist, create a new one
        new_df = pd.DataFrame(data)
        new_df.to_excel(filename, index=False)

    print(f"Extraction complete! Data saved to {filename}.")


# Function to run the scraper
def run_scraper():
    print("Running scraper at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    main_scraper_function()  # Calls the defined function

# Schedule the scraper to run every day at 3 AM 
schedule.every().day.at("03:00").do(run_scraper)


# Keep the script running to check and execute scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute


