"""デイリー自動実行スクリプト。"""

from __future__ import annotations

import time
from pathlib import Path

import schedule

from src.cli import load_config
from src.report import output_report
from src.screener import StockScreener

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


def run_daily() -> None:
    """日次ジョブを1回実行する。"""
    config = load_config(CONFIG_PATH)
    rows = StockScreener(config).run()
    schedule_cfg = config.get("schedule", {})
    output_report(
        rows,
        output=schedule_cfg.get("output", "csv"),
        csv_path=schedule_cfg.get("csv_path", "daily_screening_result.csv"),
    )


def main() -> None:
    """毎日指定時刻に run_daily を実行する。"""
    config = load_config(CONFIG_PATH)
    daily_time = config.get("schedule", {}).get("daily_time", "07:00")
    schedule.every().day.at(daily_time).do(run_daily)
    print(f"デイリースケジューラを起動しました。毎日 {daily_time} に実行します。")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
