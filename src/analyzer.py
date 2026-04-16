"""代替可能性スコアリングモジュール。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_MARKET_CONCENTRATION_PENALTY_PER_PEER = 15.0
DEFAULT_SECTOR_DIVERSITY_PENALTY_PER_PEER = 20.0
DEFAULT_WEIGHT_MARKET = 0.30
DEFAULT_WEIGHT_FINANCIAL = 0.30
DEFAULT_WEIGHT_MOMENTUM = 0.25
DEFAULT_WEIGHT_DIVERSITY = 0.15


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


@dataclass
class SubstitutabilityAnalyzer:
    """複数観点から 0-100 の代替可能性スコアを算出する。"""

    config: dict[str, Any]

    def analyze(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """各銘柄のスコアを算出し、降順で返す。"""
        if not rows:
            return []

        weights = self.config.get("scoring", {}).get("weights", {})
        w_market = float(weights.get("market_concentration", DEFAULT_WEIGHT_MARKET))
        w_financial = float(weights.get("financial", DEFAULT_WEIGHT_FINANCIAL))
        w_momentum = float(weights.get("momentum", DEFAULT_WEIGHT_MOMENTUM))
        w_diversity = float(weights.get("sector_diversity", DEFAULT_WEIGHT_DIVERSITY))

        total_w = w_market + w_financial + w_momentum + w_diversity
        if total_w <= 0:
            w_market, w_financial, w_momentum, w_diversity = (
                DEFAULT_WEIGHT_MARKET,
                DEFAULT_WEIGHT_FINANCIAL,
                DEFAULT_WEIGHT_MOMENTUM,
                DEFAULT_WEIGHT_DIVERSITY,
            )
            total_w = 1.0

        min_cap = float(self.config.get("screening", {}).get("market_cap_min", 1e8))
        max_cap = float(self.config.get("screening", {}).get("market_cap_max", 2e10))
        market_penalty = float(
            self.config.get("scoring", {}).get(
                "market_concentration_penalty_per_peer",
                DEFAULT_MARKET_CONCENTRATION_PENALTY_PER_PEER,
            )
        )
        diversity_penalty = float(
            self.config.get("scoring", {}).get(
                "sector_diversity_penalty_per_peer",
                DEFAULT_SECTOR_DIVERSITY_PENALTY_PER_PEER,
            )
        )

        theme_counts: dict[str, int] = {}
        for row in rows:
            theme_counts[row.get("theme", "other")] = theme_counts.get(row.get("theme", "other"), 0) + 1

        scored: list[dict[str, Any]] = []
        for row in rows:
            peers = float(theme_counts.get(row.get("theme", "other"), 1))

            market_concentration_score = _clamp(100 - ((peers - 1) * market_penalty))
            financial_score = self._financial_score(row, min_cap=min_cap, max_cap=max_cap)
            momentum_score = self._momentum_score(row)
            sector_diversity_score = _clamp(100 - ((peers - 1) * diversity_penalty))

            score = (
                market_concentration_score * w_market
                + financial_score * w_financial
                + momentum_score * w_momentum
                + sector_diversity_score * w_diversity
            ) / total_w

            scored.append(
                {
                    **row,
                    "market_concentration_score": round(market_concentration_score, 2),
                    "financial_score": round(financial_score, 2),
                    "momentum_score": round(momentum_score, 2),
                    "sector_diversity_score": round(sector_diversity_score, 2),
                    "substitutability_score": round(_clamp(score), 2),
                }
            )

        return sorted(scored, key=lambda x: x["substitutability_score"], reverse=True)

    @staticmethod
    def _financial_score(row: dict[str, Any], min_cap: float, max_cap: float) -> float:
        market_cap = float(row.get("market_cap", 0.0))
        revenue_growth = float(row.get("revenue_growth", 0.0))
        profit_margin = float(row.get("profit_margin", 0.0))

        if market_cap < min_cap:
            cap_score = 40
        elif market_cap > max_cap:
            cap_score = 30
        else:
            cap_score = 100

        growth_score = _clamp(50 + revenue_growth)  # 0%成長を中立(50)として評価
        margin_score = _clamp(50 + (profit_margin * 2))  # 利益率は影響をやや強めるため2倍
        return (cap_score * 0.4) + (growth_score * 0.35) + (margin_score * 0.25)

    @staticmethod
    def _momentum_score(row: dict[str, Any]) -> float:
        momentum = float(row.get("momentum", 0.0))
        volatility = float(row.get("volatility", 0.0))

        trend_score = _clamp(50 + momentum)
        vol_score = _clamp(100 - (volatility * 1.2))
        return (trend_score * 0.7) + (vol_score * 0.3)
