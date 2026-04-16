"""CLI エントリーポイント。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from .report import output_report
from .screener import StockScreener


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


def load_config(config_path: str | Path) -> dict[str, Any]:
    """YAML設定を読み込む。"""
    with Path(config_path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@click.group()
def cli() -> None:
    """米国エネルギー新興株の代替可能性スクリーナー。"""


@cli.command("run")
@click.option("--config", "config_path", default=str(DEFAULT_CONFIG_PATH), show_default=True, help="設定ファイル")
@click.option(
    "--output",
    type=click.Choice(["console", "csv"], case_sensitive=False),
    default=None,
    help="出力形式",
)
@click.option("--csv-path", default=None, help="CSV出力パス（output=csv時）")
def run_command(config_path: str, output: str | None, csv_path: str | None) -> None:
    """オンデマンドでスクリーニングを実行する。"""
    config = load_config(config_path)
    screener = StockScreener(config)
    results = screener.run()

    report_cfg = config.get("report", {})
    final_output = str(output or report_cfg.get("default_output", "console")).lower()
    final_csv_path = csv_path or report_cfg.get("csv_path", "screening_result.csv")

    output_report(results, output=final_output, csv_path=final_csv_path)


if __name__ == "__main__":
    cli()
