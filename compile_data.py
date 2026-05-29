import os
import re
import json
import pandas as pd
from price_scraper_core import get_domain, clean_price_to_float, load_websites

def compile_dashboard_only():
    print("========================================")
    print("  Dashboard Data Compiler Starting...   ")
    print("========================================")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    excel_filename = os.path.join(base_path, "price_extractor.xlsx")
    json_filename = os.path.join(base_path, "data.json")
    js_filename = os.path.join(base_path, "data.js")
    
    if not os.path.exists(excel_filename):
        print(f"❌ Error: {excel_filename} does not exist. Cannot compile.")
        return
        
    print(f"Loading historical Excel registry: {excel_filename}")
    df = pd.read_excel(excel_filename)
    
    print("Loading active websites configurations for status matching...")
    active_websites = load_websites()
    active_urls = {site["url"] for site in active_websites}
    print(f"Found {len(active_urls)} active products in websites.xlsx.")
    
    # Identify price history columns
    price_cols = [col for col in df.columns if col.startswith("Price_")]
    
    # Sort price columns chronologically by date in the name (e.g. Price_2025-02-12 14:57)
    def get_date_key(col_name):
        match = re.search(r'Price_(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})', col_name)
        return match.group(1) if match else col_name
        
    price_cols.sort(key=get_date_key)
    print(f"Detected {len(price_cols)} historical scraping runs.")
    
    json_data = []
    
    for idx, row in df.iterrows():
        url = row["URL"]
        name = row["Product Name"] if pd.notna(row["Product Name"]) else "Unknown Product"
        domain = get_domain(url)
        
        # Build history sequence
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
                
        # Resolve status based on websites.xlsx
        status = "active" if url in active_urls else "inactive"
        error_msg = "" if status == "active" else "Archived: Product removed from websites configuration."
        
        json_data.append({
            "url": url,
            "name": name,
            "domain": domain,
            "current_price": current_price,
            "status": status,
            "error_message": error_msg,
            "last_updated": datetime_now_str(),
            "history": history
        })
        
    # Write JSON database
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)
    print(f"✅ data.json written successfully: {json_filename}")
    
    # Write CORS bypass JS bundle
    with open(js_filename, "w", encoding="utf-8") as jf:
        jf.write(f"const priceTrackerData = {json.dumps(json_data, indent=2)};")
    print(f"✅ data.js written successfully: {js_filename}")
    print("========================================")
    print("  Compiler Finished Successfully!       ")
    print("========================================")

def datetime_now_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")

if __name__ == "__main__":
    compile_dashboard_only()
