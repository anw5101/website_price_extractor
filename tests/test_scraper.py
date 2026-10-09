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
        
        # Test bot blocks
        valid, msg = price_scraper_core.validate_product_name("Access Denied")
        self.assertFalse(valid)
        self.assertIn("access denied", msg.lower())
        
        valid, msg = price_scraper_core.validate_product_name("Please verify you are human")
        self.assertFalse(valid)
        self.assertIn("verify you are human", msg.lower())
        
        # Test missing / empty
        valid, msg = price_scraper_core.validate_product_name("")
        self.assertFalse(valid)
        self.assertIn("Invalid length", msg)

    def test_validate_price(self):
        valid, _ = price_scraper_core.validate_price("$1,049.00")
        self.assertTrue(valid)
        
        # Test missing / non-numerical (Out of stock)
        valid, msg = price_scraper_core.validate_price("Out of stock")
        self.assertFalse(valid)
        self.assertIn("numerical digits", msg)
        
        valid, msg = price_scraper_core.validate_price("")
        self.assertFalse(valid)
        self.assertIn("empty", msg.lower())
        
        # Test bot blocks inside price element
        valid, msg = price_scraper_core.validate_price("Cloudflare protection")
        self.assertFalse(valid)
        self.assertIn("cloudflare", msg.lower())

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

    def test_check_for_anomaly(self):
        # Normal fluctuation, no anomaly
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$10.00", 12.00)
        self.assertFalse(is_anomaly)
        
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$15.00", 12.00)
        self.assertFalse(is_anomaly)
        
        # Anomaly: Price drop > 80% (lower bound)
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$2.00", 100.00)
        self.assertTrue(is_anomaly)
        self.assertIn("dropped massively", reason)
        
        # Anomaly: Price increase > 400% (upper bound)
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$501.00", 100.00)
        self.assertTrue(is_anomaly)
        self.assertIn("increased massively", reason)
        
        # Edge cases: Missing or non-positive historical price
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$10.00", None)
        self.assertFalse(is_anomaly)
        
        is_anomaly, reason = price_scraper_core.check_for_anomaly("$10.00", 0)
        self.assertFalse(is_anomaly)
        
        # Edge case: Invalid scraped price string
        is_anomaly, reason = price_scraper_core.check_for_anomaly("Not a price", 10.00)
        self.assertFalse(is_anomaly)

if __name__ == '__main__':
    unittest.main()
