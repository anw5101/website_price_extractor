from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd

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
# Sara Lee Brioche Hamburger Buns
   {
        "url": "https://www.walmart.com/ip/Sara-Lee-Artesano-Brioche-Hamburger-Buns-8-count-16-oz/602085634",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# GV Mayonnaise 
 {
        "url": "https://www.walmart.com/ip/Great-Value-Mayonnaise-30-fl-oz/17056888",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# GV Canned Pears 
{
        "url": "https://www.walmart.com/ip/Great-Value-Pear-Halves-in-Pear-Juice-15-oz/10415589",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# Romaine Lettuce Hearts 3x 
{
        "url": "https://www.walmart.com/ip/Fresh-Romaine-Lettuce-Hearts-3-Count-Each/10532755",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# GV Oven Roasted Turkey Breast 
 {
        "url": "https://www.walmart.com/ip/Great-Value-Thin-Sliced-Oven-Roasted-Turkey-Breast-Family-Pack-16-oz-Plastic-Tub-9-Grams-of-Protein-per-2-oz-Serving/47394316",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# GV Cottage Cheese
{
        "url": "https://www.walmart.com/ip/Great-Value-4-Milkfat-Minimum-Small-Curd-Cottage-Cheese-24-oz/10315022",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# Fairlife Skim Milk
    {
        "url": "https://www.walmart.com/ip/Fairlife-Fat-Free-Ultra-Filtered-Milk-52-fl-oz/43984342",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# Banana 
{
        "url": "https://www.walmart.com/ip/Fresh-Banana-Fruit-Each/44390948",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# Clementines 
 {
        "url": "https://www.walmart.com/ip/Clementines-3-lbs/11025598",
        "xpaths": {
            "Product Name": '//*[@id="main-title"]',
            "Price": '//*[@id="maincontent"]/section/main/div[2]/div[2]/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span'
        }
    },
# 90/10 Ground Beef
{
        "url": "https://www.hy-vee.com/aisles-online/p/31823/Certified-Ground-Round-90-Lean-10-Fat",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
        }
    },
# Boneless Chicken Breast 
{
        "url": "https://www.hy-vee.com/aisles-online/p/65791/Boneless-Skinless-Chicken-Breast",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
        }
    },
# Ram 1500 
 {
        "url": "https://www.ramtrucks.com/ram-1500.html",
        "xpaths": {
            "Product Name": '//*[@id="secondary_navigation"]/div/div/div/div[1]/div[1]/div/div[1]/div/div[3]',
            "Price": '//*[@id="blurb_rail_copy_copy"]/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div[2]'
        }
    },
# Chevrolet Silverado 1500 
 {
        "url": "https://www.chevrolet.com/trucks/silverado/1500",
        "xpaths": {
            "Product Name": '//*[@id="gb-main-content"]/gb-adv-grid[4]/adv-col/div/gb-adv-grid/adv-col/div/gb-adv-grid/adv-col/div/div[1]/div/p/span',
            "Price": '//*[@id="gb-main-content"]/gb-adv-grid[2]/adv-col[2]/div/gb-adv-grid/adv-col[1]/div/div/div/p/span'
        }
    },
# 2x4 8' Lumber 
 {
        "url": "https://www.menards.com/main/building-materials/lumber-boards/dimensional-lumber/2-x-4-construction-framing-lumber/1021101/p-1444451086852-c-13125.htm",
        "xpaths": {
            "Product Name": '//*[@id="itemDetails"]/div/div[2]/div/div[1]/h1',
            "Price": '//*[@id="itemDetails"]/div/div[2]/div/div[3]/div[2]/div/div[1]/span[2]'
        }
    },
# Maple Syrup 
 {
        "url": "https://www.hy-vee.com/aisles-online/p/22365/HyVee-Select-100-Pure-Maple-Syrup",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '//*[@id="main"]/div/div/div[2]/div[2]/p[1]'
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

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Run in the background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Store extracted data
data = []

for site in websites:
    url = site["url"]
    print(f"Opening: {url}")
    driver.get(url)

    site_data = {"URL": url}

    for label, xpath in site["xpaths"].items():
        try:
            element = driver.find_element(By.XPATH, xpath)
            site_data[label] = element.text.strip()
        except Exception as e:
            site_data[label] = "Not found"

    data.append(site_data)

# Close browser
driver.quit()

# Save data to Excel
df = pd.DataFrame(data)
df.to_excel("price_extractor.xlsx", index=False)

print("Extraction complete! Data saved to price_extractor.xlsx")
