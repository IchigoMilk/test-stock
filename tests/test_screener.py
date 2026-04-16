import unittest

from src.screener import StockScreener


class DummyFetcher:
    def get_energy_tickers(self):
        return ["A", "B", "C"]

    def fetch_many(self, tickers):
        return [
            {"ticker": "A", "market_cap": 5e9, "theme": "hydrogen"},
            {"ticker": "B", "market_cap": 3e7, "theme": "hydrogen"},
            {"ticker": "C", "market_cap": 8e9, "theme": "battery"},
        ]


class DummyAnalyzer:
    def analyze(self, rows):
        return [{**row, "substitutability_score": 50} for row in rows]


class TestStockScreener(unittest.TestCase):
    def test_run_filters_by_market_cap(self):
        screener = StockScreener({"screening": {"market_cap_min": 1e8, "market_cap_max": 2e10, "top_n": 10}})
        screener.data_fetcher = DummyFetcher()
        screener.analyzer = DummyAnalyzer()

        result = screener.run()

        self.assertEqual(2, len(result))
        self.assertEqual({"A", "C"}, {r["ticker"] for r in result})


if __name__ == "__main__":
    unittest.main()
