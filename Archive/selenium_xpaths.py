from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the website
url = "https://www.kwiktrip.com/locator/store?id=1056"
driver.get(url)

# Extract data using XPath
try:
    element = driver.find_element(By.XPATH, '//*[@id="storeInfoApp"]/div/div[2]/div[1]/div[2]/div[1]/div[3]/span[2]')
    extracted_data = element.text
except Exception as e:
    extracted_data = f"Error: {str(e)}"

# Close the browser
driver.quit()

# Output result
print("Extracted Data:", extracted_data)

with open("output.csv", "w") as file:
    file.write(extracted_data)

print("Data saved to output.xlsx!")

