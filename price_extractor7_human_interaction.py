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
import random

# Location (Modify for your needs)
latitude = 41.616788   # Waukee, IA
longitude = -93.854709 # Waukee, IA 
accuracy = 100         # Meters

# Function to simulate human-like interaction
def human_like_interaction(driver):
    actions = ActionChains(driver)
    
    # Simulate random mouse movements
    for _ in range(random.randint(3, 7)):
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        actions.move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(0.3, 1.5))

    # Simulate scrolling
    scroll_height = random.randint(200, 800)
    driver.execute_script(f"window.scrollBy(0, {scroll_height});")
    time.sleep(random.uniform(1, 3))

    print("✅ Simulated human-like interaction.")

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
# Cap N Crunch Cereal 
        {
        "url": "https://www.walmart.com/ip/Cap-n-Crunch-Sweetened-Corn-Oat-Cereal-22-1oz-Single-Pack/168489631",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
### Sara Lee Brioche Hamburger Buns
##   {
##        "url": "https://www.walmart.com/ip/Sara-Lee-Artesano-Brioche-Hamburger-Buns-8-count-16-oz/602085634",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### GV Mayonnaise 
## {
##        "url": "https://www.walmart.com/ip/Great-Value-Mayonnaise-30-fl-oz/17056888",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### GV Canned Pears 
##{
##        "url": "https://www.walmart.com/ip/Great-Value-Pear-Halves-in-Pear-Juice-15-oz/10415589",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### Romaine Lettuce Hearts 3x 
##{
##        "url": "https://www.walmart.com/ip/Fresh-Romaine-Lettuce-Hearts-3-Count-Each/10532755",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### GV Oven Roasted Turkey Breast 
## {
##        "url": "https://www.walmart.com/ip/Great-Value-Thin-Sliced-Oven-Roasted-Turkey-Breast-Family-Pack-16-oz-Plastic-Tub-9-Grams-of-Protein-per-2-oz-Serving/47394316",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### GV Cottage Cheese
##{
##        "url": "https://www.walmart.com/ip/Great-Value-4-Milkfat-Minimum-Small-Curd-Cottage-Cheese-24-oz/10315022",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### Fairlife Skim Milk
##    {
##        "url": "https://www.walmart.com/ip/Fairlife-Fat-Free-Ultra-Filtered-Milk-52-fl-oz/43984342",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### Banana 
##{
##        "url": "https://www.walmart.com/ip/Fresh-Banana-Fruit-Each/44390948",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### Clementines 
## {
##        "url": "https://www.walmart.com/ip/Clementines-3-lbs/11025598",
##        "xpaths": {
##            "Product Name": '//*[@id="main-title"]',
##            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
##        }
##    },
### 90/10 Ground Beef
##{
##        "url": "https://www.hy-vee.com/aisles-online/p/31823/Certified-Ground-Round-90-Lean-10-Fat",
##        "xpaths": {
##            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
##            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
##        }
##    },
### Boneless Chicken Breast 
##{
##        "url": "https://www.hy-vee.com/aisles-online/p/65791/Boneless-Skinless-Chicken-Breast",
##        "xpaths": {
##            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
##            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
##        }
##    },
### Ram 1500 
## {
##        "url": "https://www.ramtrucks.com/ram-1500.html",
##        "xpaths": {
##            "Product Name": '//*[@id="secondary_navigation"]/div/div/div/div[1]/div[1]/div/div[1]/div/div[3]',
##            "Price": '//*[@id="blurb_rail_copy_copy"]/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div[2]'
##        }
##    },
### Chevrolet Silverado 1500 
## {
##        "url": "https://www.chevrolet.com/trucks/silverado/1500",
##        "xpaths": {
##            "Product Name": '//*[@id="gb-main-content"]/gb-adv-grid[4]/adv-col/div/gb-adv-grid/adv-col/div/gb-adv-grid/adv-col/div/div[1]/div/p/span',
##            "Price": '//*[@id="gb-main-content"]/gb-adv-grid[2]/adv-col[2]/div/gb-adv-grid/adv-col[1]/div/div/div/p/span'
##        }
##    },
### 2x4 8' Lumber 
## {
##        "url": "https://www.menards.com/main/building-materials/lumber-boards/dimensional-lumber/2-x-4-construction-framing-lumber/1021101/p-1444451086852-c-13125.htm",
##        "xpaths": {
##            "Product Name": '//*[@id="itemDetails"]/div/div[2]/div/div[1]/h1',
##            "Price": '//*[@id="itemDetails"]/div/div[2]/div/div[3]/div[2]/div/div[1]/span[2]'
##        }
##    },
### Maple Syrup 
## {
##        "url": "https://www.hy-vee.com/aisles-online/p/22365/HyVee-Select-100-Pure-Maple-Syrup",
##        "xpaths": {
##            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
##            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
##        }
##    },
### Eggs 
##     {
##         "url": "https://www.hy-vee.com/aisles-online/p/2849570/Thats-Smart-Large-Shell-Eggs",
##         "xpaths": {
##             "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
##             "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
##         }
##     },
    
    # The below lines can be used to copy/paste to add new products to the website query. 
    # {
    #     "url": "",
    #     "xpaths": {
    #         "Product Name": '',
    #         "Price": ''
    #     }
    # },
]

# Function to initialize the WebDriver with proxy and options
def initialize_driver(proxy=None):
    options = Options()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')  # Set proxy server

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection

    # Use a normal user-agent for better evasion of bot detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

    # Non-headless mode to mimic real user browsing
    # options.add_argument("--headless")  # Comment out this line to disable headless mode

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

# Store extracted data
data = []

for site in websites:
    url = site["url"]
    print(f"Opening: {url}")
    
    # Initialize a new driver for each website
    driver = initialize_driver()
    driver.get(url)

    site_data = {"URL": url}

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

# Save data to Excel
df = pd.DataFrame(data)
df.to_excel("price_extractor.xlsx", index=False)

print("Extraction complete! Data saved to price_extractor.xlsx")
