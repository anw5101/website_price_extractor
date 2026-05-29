from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import time
import os
import random
import re
from datetime import datetime
from urllib.parse import urlparse

# Latitude and Longitude for geolocation spoofing if needed (Waukee, IA)
latitude = 41.616788
longitude = -93.854709
accuracy = 100

def get_domain(url):
    """Extracts a clean domain name from a URL to use as a store badge."""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            return netloc[4:]
        return netloc
    except Exception:
        return "unknown"

def load_websites(filename="websites.xlsx"):
    """Loads URL and XPath configurations from the input Excel spreadsheet."""
    # Try resolving path absolute or relative
    base_path = "/Users/anw5101/GitHub/website_price_extractor"
    path = os.path.join(base_path, filename) if not os.path.exists(filename) else filename
    
    if not os.path.exists(path):
        print(f"Error: {path} not found!")
        return []
    
    df = pd.read_excel(path)
    websites = []
    
    for _, row in df.iterrows():
        if pd.isna(row["URL"]) or pd.isna(row["Product Name XPath"]) or pd.isna(row["Price XPath"]):
            continue  # Skip rows with missing configuration data
        
        websites.append({
            "url": row["URL"],
            "xpaths": {
                "Product Name": row["Product Name XPath"],
                "Price": row["Price XPath"]
            }
        })
    
    return websites

def initialize_driver():
    """Initializes a headless Chrome WebDriver configured to avoid bot detection."""
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Headless mode for cloud and background execution
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Configure stealth parameters to prevent anti-bot detection
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

def validate_product_name(name):
    """Checks if the scraped product name appears genuine or indicates an error/block."""
    if not name or len(name) < 2 or len(name) > 150:
        return False, f"Invalid length ({len(name) if name else 0} chars)."
    
    # Standard bot detection, captcha, and error messages
    block_signals = [
        "cloudflare", "verify you are human", "access denied", "checking your browser",
        "robot", "security check", "ddos protection", "cookie consent", "enable javascript",
        "attention required", "just a moment", "site maintenance", "something went wrong"
    ]
    lower_name = name.lower()
    for signal in block_signals:
        if signal in lower_name:
            return False, f"Detected bot protection or page block string: '{signal}'"
            
    return True, "Valid"

def validate_price(price_str):
    """Validates the scraped price string using formatting and numerical heuristic rules."""
    if not price_str:
        return False, "Price string is empty."
    
    cleaned = price_str.strip().replace("\n", " ").replace("\r", " ")
    lower_price = cleaned.lower()
    
    # Check for general blocker message strings in the scraped element
    block_signals = [
        "cloudflare", "verify you are human", "access denied", "checking your browser",
        "robot", "security check", "cookie consent", "enable javascript", "just a moment"
    ]
    for signal in block_signals:
        if signal in lower_price:
            return False, f"Detected system block string: '{signal}'"
            
    # Price must contain at least one numerical digit
    if not any(char.isdigit() for char in cleaned):
        return False, "Price does not contain any numerical digits."
        
    if len(cleaned) > 50:
        return False, "Price string is too long (above 50 chars), likely parsed parent text."
        
    return True, "Valid"

def clean_price_to_float(price_str):
    """Helper to convert formatted pricing strings (e.g. '$2.87', '32¢ ea.') into clean floats."""
    if pd.isna(price_str):
        return None
    s = str(price_str).strip()
    if s.lower() in ["not found", "error", "failed", "invalid data", "nan", ""]:
        return None
    try:
        # Check for cent values without dollar symbols
        if "¢" in s and "$" not in s:
            nums = re.findall(r'\d+(?:\.\d+)?', s)
            if nums:
                return float(nums[0]) / 100.0
        
        # Standard decimal/integer search
        nums = re.findall(r'\d+(?:\.\d+)?', s)
        if nums:
            return float(nums[0])
    except Exception:
        pass
    return None

def extract_json_ld_metadata(html_content):
    """Attempts to extract product name and price from JSON-LD schema.org markup."""
    scripts = re.findall(r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', html_content, re.DOTALL)
    extracted_name = None
    extracted_price = None
    
    for script in scripts:
        try:
            data = json.loads(script.strip())
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    name = item.get("name")
                    if name:
                        import html as html_lib
                        extracted_name = html_lib.unescape(name)
                        
                    offers = item.get("offers")
                    if isinstance(offers, dict):
                        price = offers.get("price")
                        if price:
                            extracted_price = str(price)
                    elif isinstance(offers, list):
                        for offer in offers:
                            if isinstance(offer, dict):
                                price = offer.get("price")
                                if price:
                                    extracted_price = str(price)
        except Exception:
            pass
            
    return extracted_name, extracted_price

def update_excel_and_json(data):
    """Updates the historical Excel sheet and compiles dashboard-ready JSON data."""
    base_path = "/Users/anw5101/GitHub/website_price_extractor"
    excel_filename = os.path.join(base_path, "price_extractor.xlsx")
    json_filename = os.path.join(base_path, "data.json")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_price_col = f"Price_{timestamp}"
    
    # 1. Align Excel Data
    new_run_df = pd.DataFrame(data)
    new_data_to_merge = pd.DataFrame({
        "URL": new_run_df["URL"],
        "Temp_Name": new_run_df["Product Name"],
        new_price_col: new_run_df["Price"]
    })
    
    if os.path.exists(excel_filename):
        existing_df = pd.read_excel(excel_filename)
        
        # Clean any historical duplicate product name columns to avoid endless growth
        cols_to_keep = []
        for col in existing_df.columns:
            if col == "URL":
                cols_to_keep.append(col)
            elif col == "Product Name":
                cols_to_keep.append(col)
            elif col.startswith("Price_"):
                cols_to_keep.append(col)
                
        existing_df = existing_df[cols_to_keep]
        
        # Outer merge aligns matching URLs, appends new ones, and sets past entries of new items to NaN
        merged_df = pd.merge(existing_df, new_data_to_merge, on="URL", how="outer")
        
        # Resolve static Product Name
        if "Product Name" not in merged_df:
            merged_df["Product Name"] = merged_df["Temp_Name"]
        else:
            merged_df["Product Name"] = merged_df["Product Name"].fillna(merged_df["Temp_Name"])
            
            # Update product name if current scrape is a successful string
            for idx, row in merged_df.iterrows():
                t_name = row["Temp_Name"]
                if pd.notna(t_name) and t_name not in ["Not found", "Error", ""]:
                    merged_df.at[idx, "Product Name"] = t_name
                    
        merged_df = merged_df.drop(columns=["Temp_Name"])
    else:
        merged_df = pd.DataFrame({
            "URL": new_run_df["URL"],
            "Product Name": new_run_df["Product Name"],
            new_price_col: new_run_df["Price"]
        })
        
    # Sort price columns chronologically by date
    price_cols = [c for c in merged_df.columns if c.startswith("Price_")]
    def get_date_key(col_name):
        match = re.search(r'Price_(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})', col_name)
        return match.group(1) if match else col_name
        
    price_cols.sort(key=get_date_key)
    
    final_cols = ["URL", "Product Name"] + price_cols
    final_cols = [c for c in final_cols if c in merged_df.columns]
    merged_df = merged_df[final_cols]
    
    merged_df.to_excel(excel_filename, index=False)
    print(f"Excel record updated at: {excel_filename}")
    
    # 2. Compile Dashboard JSON (data.json)
    json_data = []
    
    # Index the current run metadata by URL for quick status updates
    status_map = {row["URL"]: {"Status": row["Status"], "Error": row["Error Message"]} for row in data}
    
    for _, row in merged_df.iterrows():
        url = row["URL"]
        name = row["Product Name"] if pd.notna(row["Product Name"]) else "Unknown Product"
        domain = get_domain(url)
        
        # Build history sequence by parsing all columns matching 'Price_'
        history = []
        current_price = "Not found"
        
        for p_col in price_cols:
            p_val = row[p_col]
            if pd.notna(p_val) and str(p_val).strip() not in ["Not found", "Error", ""]:
                # Extract date from price column name
                date_match = re.search(r'Price_(\d{4}-\d{2}-\d{2})', p_col)
                date_str = date_match.group(1) if date_match else "unknown"
                
                # Convert price text to numerical float
                numeric_val = clean_price_to_float(p_val)
                if numeric_val is not None:
                    history.append({
                        "date": date_str,
                        "price": numeric_val,
                        "raw_price": str(p_val)
                    })
                current_price = str(p_val)
                
        # Resolve scraper status
        meta = status_map.get(url, {"Status": "inactive", "Error": ""})
        
        # If scraper didn't run on this product in the current run (e.g. deleted from websites.xlsx)
        if url not in status_map:
            meta["Status"] = "inactive"
            meta["Error"] = "Product has been removed from active websites config."
            
        json_data.append({
            "url": url,
            "name": name,
            "domain": domain,
            "current_price": current_price,
            "status": meta["Status"],
            "error_message": meta["Error"],
            "last_updated": timestamp,
            "history": history
        })
        
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)
    print(f"Dashboard JSON updated at: {json_filename}")
    
    # 3. Compile data.js to bypass file:// protocol CORS checks locally
    js_filename = os.path.join(base_path, "data.js")
    with open(js_filename, "w", encoding="utf-8") as jf:
        jf.write(f"const priceTrackerData = {json.dumps(json_data, indent=2)};")
    print(f"Dashboard Javascript JSON bundle updated at: {js_filename}")

def main_scraper_function():
    """Loops through all active configurations, scrapes elements, validates data, and outputs results."""
    print("Loading active websites configurations...")
    websites = load_websites()
    
    if not websites:
        print("No active configurations found in websites.xlsx. Exiting.")
        return
        
    print(f"Scraper initialized. Running headless query for {len(websites)} URLs...")
    data = []
    driver = None
    
    try:
        driver = initialize_driver()
        
        for idx, site in enumerate(websites):
            url = site["url"]
            print(f"[{idx+1}/{len(websites)}] Querying: {url}")
            
            scraped_name = "Not found"
            scraped_price = "Not found"
            status = "active"
            error_message = ""
            
            try:
                driver.get(url)
                # Mimic standard network wait
                time.sleep(3)
                
                # Check for bot block pages/Cloudflare
                page_title = driver.title.lower()
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                
                cloudflare_blocked = (
                    "cloudflare" in page_title or 
                    "verify you are human" in page_title or 
                    "just a moment" in page_title or
                    "checking your browser" in body_text or
                    "access denied" in body_text
                )
                
                if cloudflare_blocked:
                    status = "blocked"
                    error_message = "Headless browser was blocked by anti-bot page (e.g., Cloudflare check)."
                    print(f"  ❌ Blocked: {error_message}")
                else:
                    # 1. Try primary XPaths first
                    scraped_name = "Not found"
                    scraped_price = "Not found"
                    xpath_name_failed = False
                    xpath_price_failed = False
                    
                    # Try Product Name XPath
                    xpath_name = site["xpaths"]["Product Name"]
                    try:
                        element_name = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath_name))
                        )
                        scraped_name = element_name.text.strip()
                        name_valid, _ = validate_product_name(scraped_name)
                        if not name_valid or not scraped_name:
                            xpath_name_failed = True
                    except Exception:
                        xpath_name_failed = True
                        
                    # Try Price XPath
                    xpath_price = site["xpaths"]["Price"]
                    try:
                        element_price = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath_price))
                        )
                        scraped_price = element_price.text.strip()
                        price_valid, _ = validate_price(scraped_price)
                        if not price_valid or not scraped_price:
                            xpath_price_failed = True
                    except Exception:
                        xpath_price_failed = True
                        
                    # 2. Trigger Self-Healing Fallbacks if either XPath fails!
                    if xpath_name_failed or xpath_price_failed:
                        print("  🔍 Primary XPath failed/returned invalid data. Activating self-healing fallback system...")
                        
                        # Fallback A: JSON-LD metadata parsing
                        html_content = driver.page_source
                        json_name, json_price = extract_json_ld_metadata(html_content)
                        
                        if xpath_name_failed and json_name:
                            scraped_name = json_name
                            xpath_name_failed = False
                            print(f"  ✨ Recovered Product Name from JSON-LD Schema: '{scraped_name}'")
                            
                        if xpath_price_failed and json_price:
                            # Format to look like standard currency
                            scraped_price = f"${float(json_price):.2f}" if json_price.replace(".", "", 1).isdigit() else json_price
                            xpath_price_failed = False
                            print(f"  ✨ Recovered Price from JSON-LD Schema: '{scraped_price}'")
                            
                        # Fallback B: DOM Tag Fallbacks
                        # Fallback B1: Product Name H1 tag lookup
                        if xpath_name_failed:
                            try:
                                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                                for h1 in h1_elements:
                                    h1_text = h1.text.strip()
                                    h1_valid, _ = validate_product_name(h1_text)
                                    if h1_valid and h1_text:
                                        scraped_name = h1_text
                                        xpath_name_failed = False
                                        print(f"  ✨ Recovered Product Name from H1 element fallback: '{scraped_name}'")
                                        break
                            except Exception:
                                pass
                                
                        # Fallback B2: DOM Price-class lookup
                        if xpath_price_failed:
                            try:
                                price_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'price') or contains(@class, 'Price')]")
                                for pe in price_elements:
                                    pe_text = pe.text.strip()
                                    pe_valid, _ = validate_price(pe_text)
                                    # Must match a simple numerical price validation to avoid parent container noise
                                    if pe_valid and pe_text and re.search(r'\d', pe_text) and len(pe_text) < 15:
                                        scraped_price = pe_text
                                        xpath_price_failed = False
                                        print(f"  ✨ Recovered Price from Price-class element fallback: '{scraped_price}'")
                                        break
                            except Exception:
                                pass
                                
                    # 3. Final Validation & State Resolution
                    name_valid, name_reason = validate_product_name(scraped_name)
                    price_valid, price_reason = validate_price(scraped_price)
                    
                    if xpath_name_failed or xpath_price_failed:
                        status = "xpath_error"
                        error_message = ""
                        if xpath_name_failed:
                            error_message += "Product Name XPath could not be resolved or recovered."
                        if xpath_price_failed:
                            error_message += (" | " if error_message else "") + "Price XPath could not be resolved or recovered."
                    elif not name_valid or not price_valid:
                        status = "invalid_data"
                        error_message = ""
                        if not name_valid:
                            error_message += f"Product Name validation failure: {name_reason}"
                        if not price_valid:
                            error_message += (" | " if error_message else "") + f"Price validation failure: {price_reason}"
                    else:
                        status = "active"
                        error_message = ""
                        
            except Exception as e:
                status = "failed"
                error_message = f"Browser execution failed: {str(e)}"
                print(f"  ❌ Navigation Error: {error_message}")
                
            # Log output status
            site_data = {
                "URL": url,
                "Product Name": scraped_name,
                "Price": scraped_price,
                "Status": status,
                "Error Message": error_message
            }
            print(f"  Result: {scraped_name} -> {scraped_price} (Status: {status})")
            data.append(site_data)
            
            # Mimic human interaction and random delays
            if idx < len(websites) - 1:
                delay = random.uniform(2.5, 6.0)
                print(f"  Sleeping {delay:.2f} seconds to prevent connection throttling...")
                time.sleep(delay)
                
    finally:
        if driver:
            driver.quit()
            print("Chrome WebDriver process terminated.")
            
    # Process files
    update_excel_and_json(data)
