import unittest

from src.screener import StockScreener


class MockDataFetcher:
    def get_energy_tickers(self):
        return ["A", "B", "C", "D"]

    def fetch_many(self, tickers):
        return [
            {"ticker": "A", "market_cap": 5e9, "theme": "hydrogen"},
            {"ticker": "B", "market_cap": 3e7, "theme": "hydrogen"},
            {"ticker": "C", "market_cap": 8e9, "theme": "battery"},
            {"ticker": "D", "market_cap": 9e9, "theme": "ccs"},
        ]


class MockAnalyzer:
    def analyze(self, rows):
        with_scores = []
        for row in rows:
            score = {"C": 90, "D": 70}.get(row["ticker"], 50)
            with_scores.append({**row, "substitutability_score": score})
        return sorted(with_scores, key=lambda r: r["substitutability_score"], reverse=True)


class TestStockScreener(unittest.TestCase):
    def test_run_filters_and_sorts_by_score(self):
        screener = StockScreener({"screening": {"market_cap_min": 1e8, "market_cap_max": 2e10, "top_n": 10}})
        screener.data_fetcher = MockDataFetcher()
        screener.analyzer = MockAnalyzer()

        result = screener.run()

        self.assertEqual(3, len(result))
        self.assertEqual({"A", "C", "D"}, {r["ticker"] for r in result})
        self.assertEqual(["C", "D", "A"], [r["ticker"] for r in result])
        self.assertEqual([90, 70, 50], [r["substitutability_score"] for r in result])

    def test_run_applies_top_n_limit(self):
        screener = StockScreener({"screening": {"market_cap_min": 1e8, "market_cap_max": 2e10, "top_n": 2}})
        screener.data_fetcher = MockDataFetcher()
        screener.analyzer = MockAnalyzer()

        result = screener.run()

        self.assertEqual(2, len(result))
        self.assertEqual(["C", "D"], [r["ticker"] for r in result])
        self.assertEqual([90, 70], [r["substitutability_score"] for r in result])


if __name__ == "__main__":
    unittest.main()
