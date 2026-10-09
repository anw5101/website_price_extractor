from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get("https://www.ramtrucks.com/ram-1500.html")
time.sleep(5)
html = driver.page_source
with open("ram_page.html", "w", encoding="utf-8") as f:
    f.write(html)
driver.quit()
