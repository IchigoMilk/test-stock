"""スクリーニング実行モジュール。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .analyzer import SubstitutabilityAnalyzer
from .data_fetcher import DataFetcher


@dataclass
class StockScreener:
    """データ取得・フィルタ・スコア算出を一括実行する。"""

    config: dict[str, Any]
    data_fetcher: DataFetcher = field(init=False)
    analyzer: SubstitutabilityAnalyzer = field(init=False)

    def __post_init__(self) -> None:
        self.data_fetcher = DataFetcher(self.config)
        self.analyzer = SubstitutabilityAnalyzer(self.config)

    def run(self) -> list[dict[str, Any]]:
        """スクリーニングを実行して上位結果を返す。"""
        tickers = self.data_fetcher.get_energy_tickers()
        raw = self.data_fetcher.fetch_many(tickers)

        min_cap = float(self.config.get("screening", {}).get("market_cap_min", 1e8))
        max_cap = float(self.config.get("screening", {}).get("market_cap_max", 2e10))
        top_n = int(self.config.get("screening", {}).get("top_n", 20))

        filtered = [
            r
            for r in raw
            if min_cap <= float(r.get("market_cap", 0.0)) <= max_cap
        ]

        analyzed = self.analyzer.analyze(filtered)
        return analyzed[:top_n]
