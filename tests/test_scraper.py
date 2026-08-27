import unittest
import sys
import os
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import price_scraper_core

class DummyResponse:
    def __init__(self, text):
        self.text = text

class TestPriceScraperCore(unittest.TestCase):
    def test_get_domain(self):
        self.assertEqual(price_scraper_core.get_domain("https://www.homedepot.com/p/Samsung/123"), "homedepot.com")

    def test_validate_product_name(self):
        valid, _ = price_scraper_core.validate_product_name("Samsung 5.5 cu. ft. Washer")
        self.assertTrue(valid)
        valid, _ = price_scraper_core.validate_product_name("Access Denied")
        self.assertFalse(valid)

    def test_validate_price(self):
        valid, _ = price_scraper_core.validate_price("$1,049.00")
        self.assertTrue(valid)
        valid, _ = price_scraper_core.validate_price("Out of stock")
        self.assertFalse(valid)

    def test_clean_price_to_float(self):
        self.assertEqual(price_scraper_core.clean_price_to_float("$1,049.00"), 1049.00)
        self.assertEqual(price_scraper_core.clean_price_to_float("99¢"), 0.99)
        self.assertIsNone(price_scraper_core.clean_price_to_float(pd.NA))

    def test_extract_json_ld_metadata(self):
        html = '<html><script type="application/ld+json">{"@type": "Product", "name": "Heavy Duty", "offers": {"price": "4.99"}}</script></html>'
        name, price = price_scraper_core.extract_json_ld_metadata(html)
        self.assertEqual(name, "Heavy Duty")
        self.assertEqual(price, "4.99")

    @patch("price_scraper_core.os.environ.get")
    def test_ai_fallback_extraction(self, mock_env_get):
        mock_env_get.return_value = "fake_api_key"
        
        mock_google = MagicMock()
        mock_client = MagicMock()
        mock_google.genai.Client.return_value = mock_client
        mock_response = DummyResponse('{"product_name": "AI Found Name", "price": "$12.34"}')
        mock_client.models.generate_content.return_value = mock_response
        
        with patch.dict('sys.modules', {'google': mock_google, 'google.genai': mock_google.genai, 'google.genai.types': MagicMock(), 'pydantic': MagicMock()}):
            name, price = price_scraper_core.ai_fallback_extraction("Dummy webpage text", "http://example.com")
            
        self.assertEqual(name, "AI Found Name")
        self.assertEqual(price, "$12.34")

if __name__ == '__main__':
    unittest.main()
