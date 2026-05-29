import os
import re
import json
import time
from price_scraper_core import initialize_driver, extract_json_ld_metadata, validate_product_name, validate_price

def test_single_recovery():
    print("========================================")
    print("  Testing Self-Healing Recovery...      ")
    print("========================================")
    
    driver = None
    try:
        driver = initialize_driver()
        # Set page load timeout to prevent hanging
        driver.set_page_load_timeout(30)
        
        url = "https://www.hy-vee.com/aisles-online/p/2869496/Thats-Smart-Fat-Free-Skim-Milk"
        print(f"Opening: {url}")
        
        start_time = time.time()
        driver.get(url)
        print(f"Page loaded in {time.time() - start_time:.2f} seconds.")
        
        # Activating fallback
        print("🔍 Simulating primary XPath failure. Running self-healing fallbacks...")
        html_content = driver.page_source
        
        json_name, json_price = extract_json_ld_metadata(html_content)
        print("\n--- A: JSON-LD Recovery Results ---")
        print(f"Recovered Name: '{json_name}'")
        print(f"Recovered Price: '{json_price}'")
        
        #DOM Fallback checks
        print("\n--- B: DOM Tag Recovery Results ---")
        h1_name = None
        try:
            h1s = driver.find_elements("tag name", "h1")
            for h1 in h1s:
                txt = h1.text.strip()
                valid, _ = validate_product_name(txt)
                if valid and txt:
                    h1_name = txt
                    break
        except Exception as e:
            print("Error finding H1:", e)
        print(f"Recovered Name via H1 fallback: '{h1_name}'")
        
        price_class_val = None
        try:
            pes = driver.find_elements("xpath", "//*[contains(@class, 'price') or contains(@class, 'Price')]")
            for pe in pes:
                txt = pe.text.strip()
                valid, _ = validate_price(txt)
                if valid and txt and re.search(r'\d', txt) and len(txt) < 15:
                    price_class_val = txt
                    break
        except Exception as e:
            print("Error finding price classes:", e)
        print(f"Recovered Price via Price-class fallback: '{price_class_val}'")
        
    except Exception as e:
        print("Inspection Error:", e)
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")
    print("========================================")

if __name__ == "__main__":
    test_single_recovery()
