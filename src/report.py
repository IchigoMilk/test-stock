"""レポート出力モジュール。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def output_report(rows: list[dict], output: str = "console", csv_path: str = "screening_result.csv") -> None:
    """結果を console または csv に出力する。"""
    frame = pd.DataFrame(rows)

    if output == "csv":
        path = Path(csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        print(f"CSVに出力しました: {path}")
        return

    if frame.empty:
        print("対象銘柄がありませんでした。")
        return

    columns = [
        "ticker",
        "theme",
        "market_cap",
        "revenue_growth",
        "profit_margin",
        "momentum",
        "volatility",
        "substitutability_score",
    ]
    available_cols = [c for c in columns if c in frame.columns]
    display = frame[available_cols].copy()
    print(display.to_string(index=False))
