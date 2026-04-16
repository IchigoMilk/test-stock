import unittest

from src.analyzer import SubstitutabilityAnalyzer


class TestSubstitutabilityAnalyzer(unittest.TestCase):
    def test_analyze_returns_sorted_score_within_range(self):
        analyzer = SubstitutabilityAnalyzer(
            {
                "screening": {"market_cap_min": 1e8, "market_cap_max": 2e10},
                "scoring": {"weights": {}},
            }
        )
        rows = [
            {
                "ticker": "AAA",
                "market_cap": 5e9,
                "revenue_growth": 30,
                "profit_margin": 10,
                "momentum": 20,
                "volatility": 15,
                "theme": "hydrogen",
            },
            {
                "ticker": "BBB",
                "market_cap": 3e9,
                "revenue_growth": -10,
                "profit_margin": -5,
                "momentum": -5,
                "volatility": 40,
                "theme": "other",
            },
        ]

        result = analyzer.analyze(rows)

        self.assertEqual(2, len(result))
        self.assertGreaterEqual(result[0]["substitutability_score"], result[1]["substitutability_score"])
        for row in result:
            self.assertGreaterEqual(row["substitutability_score"], 0)
            self.assertLessEqual(row["substitutability_score"], 100)


if __name__ == "__main__":
    unittest.main()
