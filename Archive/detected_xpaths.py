import requests
import pandas as pd
from lxml import html

# Sample websites (Replace with real product pages)
websites = ["https://www.kwiktrip.com/locator/store?id=1056"]

# Function to generate potential XPath
def detect_xpath(tree, keywords):
    for tag in ["h1", "span", "div", "p"]:
        elements = tree.xpath(f"//{tag}")
        for elem in elements:
            if elem.text and any(keyword.lower() in elem.text.lower() for keyword in keywords):
                return tree.getpath(elem)  # Generate XPath dynamically
    return "Not found"

# List to store extracted data
data = []

for url in websites:
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        tree = html.fromstring(response.content)

        # Detect XPaths for title and price
        title_xpath = detect_xpath(tree, ["title", "product"])
        price_xpath = detect_xpath(tree, ["$", "price", "€", "£"])

        # Extract data
        title = tree.xpath(title_xpath + "/text()") if title_xpath != "Not found" else "Not found"
        price = tree.xpath(price_xpath + "/text()") if price_xpath != "Not found" else "Not found"

        data.append({"URL": url, "Title XPath": title_xpath, "Extracted Title": title, 
                     "Price XPath": price_xpath, "Extracted Price": price})
    except Exception as e:
        data.append({"URL": url, "Title XPath": "Error", "Extracted Title": str(e), 
                     "Price XPath": "Error", "Extracted Price": str(e)})

# Save to Excel
df = pd.DataFrame(data)
df.to_excel("detected_xpaths.xlsx", index=False)

print("XPath detection complete. Results saved to detected_xpaths.xlsx")
