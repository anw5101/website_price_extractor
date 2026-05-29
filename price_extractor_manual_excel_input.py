import sys
from price_scraper_core import main_scraper_function

if __name__ == "__main__":
    print("========================================")
    print("  Starting Manual Price Extraper Run    ")
    print("========================================")
    
    try:
        main_scraper_function()
        print("========================================")
        print("  Manual Price Extractor completed successfully! ")
        print("========================================")
    except Exception as e:
        print("\n❌ Error running scraper manual execution:")
        print(e)
        sys.exit(1)
