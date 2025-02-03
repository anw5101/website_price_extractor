from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd

# List of websites and corresponding XPaths
websites = [
    {
        "url": "https://www.kwiktrip.com/locator/store?id=1056",
        "xpaths": {
            "Product Name": '//*[@id="storeInfoApp"]/div/div[2]/div[1]/div[2]/div[1]/div[1]',
            "Price": '//*[@id="storeInfoApp"]/div/div[2]/div[1]/div[2]/div[1]/div[3]/span[2]'
        }
    },
    {
        "url": "https://www.hy-vee.com/aisles-online/p/2869496/Thats-Smart-Fat-Free-Skim-Milk",
        "xpaths": {
            "Product Name": '//*[@id="main"]/div/div/div[2]/div[2]/h1',
            "Price": '/html/body/div[1]/div/main/div/div/div/div[2]/div[2]/p[1]'
        }
    }
##    {
##        "url": "",
##        "xpaths": {
##            "Product Name": '',
##            "Price": ''
##        }
##    },
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
