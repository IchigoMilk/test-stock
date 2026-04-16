import unittest
from unittest.mock import patch

import pandas as pd

from src.data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    def test_get_energy_tickers_uses_override(self):
        fetcher = DataFetcher({"screening": {"tickers": ["plug", "be"]}})
        self.assertEqual(["BE", "PLUG"], fetcher.get_energy_tickers())

    @patch("src.data_fetcher.yf.Ticker")
    def test_fetch_ticker_metrics(self, mock_ticker_cls):
        mock_ticker = mock_ticker_cls.return_value
        mock_ticker.info = {
            "longName": "Hydrogen Test Inc.",
            "marketCap": 1000000000,
            "revenueGrowth": 0.2,
            "profitMargins": 0.1,
            "industry": "Hydrogen",
            "longBusinessSummary": "Hydrogen fuel cell company",
        }
        mock_ticker.history.return_value = pd.DataFrame({"Close": [10, 11, 12, 13]})

        fetcher = DataFetcher({"data": {"price_period": "1mo"}})
        result = fetcher.fetch_ticker_metrics("TEST")

        self.assertIsNotNone(result)
        self.assertEqual("TEST", result["ticker"])
        self.assertEqual("hydrogen", result["theme"])
        self.assertGreater(result["momentum"], 0)


if __name__ == "__main__":
    unittest.main()
