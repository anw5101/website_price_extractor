import schedule
import time
import sys
from datetime import datetime
from price_scraper_core import main_scraper_function

def run_scraper():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scraper run...")
    try:
        main_scraper_function()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scheduled scraper run completed successfully.")
    except Exception as e:
        print(f"❌ Error during scheduled scraper execution: {e}")

if __name__ == "__main__":
    print("========================================")
    print("  Price Extractor Scheduled Daemon      ")
    print("  Runs daily at 03:00 AM local time     ")
    print("========================================")
    
    # Schedule the scraper to run daily at 3 AM local time
    schedule.every().day.at("03:00").do(run_scraper)
    
    # Run once immediately to verify everything is working if desired
    # (Comment out or uncomment depending on preference)
    print("\nScraper scheduled. Daemon active and waiting for schedule trigger...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check schedule list every minute
    except KeyboardInterrupt:
        print("\nScheduled daemon stopped manually by User.")
        sys.exit(0)
