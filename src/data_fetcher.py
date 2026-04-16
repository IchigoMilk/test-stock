"""株価・ファンダメンタルズデータ取得モジュール。"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any

import pandas as pd
import yfinance as yf

DEFAULT_ENERGY_TICKERS = [
    "CEG",
    "SMR",
    "OKLO",
    "CCJ",
    "BE",
    "PLUG",
    "ENVX",
    "QS",
    "FREY",
    "EOSE",
]

THEME_KEYWORDS = {
    "renewable": ["solar", "wind", "renewable", "geothermal"],
    "hydrogen": ["hydrogen", "fuel cell"],
    "smr": ["smr", "small modular reactor", "nuclear"],
    "ccs": ["carbon capture", "ccs", "sequestration"],
    "battery": ["battery", "storage", "lithium"],
}
US_TRADING_DAYS_PER_YEAR = 252


@dataclass
class DataFetcher:
    """yfinance を利用して銘柄データを取得する。"""

    config: dict[str, Any]

    def get_energy_tickers(self) -> list[str]:
        """Energy セクター銘柄一覧を返す（config 上書き対応）。"""
        override = self.config.get("screening", {}).get("tickers", [])
        if override:
            return sorted({str(t).upper() for t in override})

        # yfinance のセクター API が使える場合は利用
        try:
            sector = yf.Sector("energy")
            top_companies = getattr(sector, "top_companies", None)
            if isinstance(top_companies, pd.DataFrame) and not top_companies.empty:
                for candidate_column in ("symbol", "ticker"):
                    if candidate_column in top_companies.columns:
                        symbols = top_companies[candidate_column].dropna().astype(str).str.upper().tolist()
                        if symbols:
                            return sorted(set(symbols))
                symbols = top_companies.index.astype(str).str.upper().tolist()
                if symbols:
                    return sorted(set(symbols))
        except Exception:
            pass

        return DEFAULT_ENERGY_TICKERS.copy()

    def fetch_many(self, tickers: list[str]) -> list[dict[str, Any]]:
        """複数銘柄の取得を行う。"""
        results: list[dict[str, Any]] = []
        for ticker in tickers:
            row = self.fetch_ticker_metrics(ticker)
            if row is not None:
                results.append(row)
        return results

    def fetch_ticker_metrics(self, ticker: str) -> dict[str, Any] | None:
        """単一銘柄の評価用メトリクスを取得する。"""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info or {}
            history = ticker_obj.history(period=self.config.get("data", {}).get("price_period", "6mo"))
        except Exception:
            return None

        if history is None or history.empty or "Close" not in history:
            return None

        close = history["Close"].dropna()
        if close.empty:
            return None

        returns = close.pct_change().dropna()
        momentum = ((close.iloc[-1] / close.iloc[0]) - 1.0) * 100 if len(close) > 1 else 0.0
        volatility = (
            float(returns.std() * sqrt(US_TRADING_DAYS_PER_YEAR) * 100) if not returns.empty else 0.0
        )

        long_text = " ".join(
            str(info.get(k, "")) for k in ("longName", "longBusinessSummary", "industry")
        ).lower()

        return {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "market_cap": float(info.get("marketCap") or 0.0),
            "revenue_growth": float(info.get("revenueGrowth") or 0.0) * 100,
            "profit_margin": float(info.get("profitMargins") or 0.0) * 100,
            "momentum": float(momentum),
            "volatility": float(volatility),
            "theme": self._infer_theme(long_text),
        }

    @staticmethod
    def _infer_theme(text: str) -> str:
        """事業説明文からセクターテーマを簡易推定する。"""
        for theme, words in THEME_KEYWORDS.items():
            if any(w in text for w in words):
                return theme
        return "other"
