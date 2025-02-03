import requests
import pandas as pd
from lxml import html

# List of URLs and their corresponding XPath expressions
websites = [
    {"url": "https://www.kwiktrip.com/locator/store?id=1056", "xpath": "/html/body/main/article/div/div/div[2]/div[1]/div[2]/div[1]/div[3]"},
]

# List to store extracted data
data = []

for site in websites:
    url = site["url"]
    xpath = site["xpath"]
    
    try:
        # Fetch the webpage
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise error for bad responses

        # Parse HTML content
        tree = html.fromstring(response.content)

        # Extract data using XPath
        extracted_data = tree.xpath(xpath)
        extracted_data = ", ".join(extracted_data) if extracted_data else "Not found"

        # Append results
        data.append({"URL": url, "XPath": xpath, "Extracted Data": extracted_data})

    except Exception as e:
        data.append({"URL": url, "XPath": xpath, "Extracted Data": f"Error: {str(e)}"})

# Save to Excel
df = pd.DataFrame(data)
df.to_excel("xpath_results.xlsx", index=False)

print("XPath data saved to xpath_results.xlsx")
