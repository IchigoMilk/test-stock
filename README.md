# test-stock

米国エネルギー関連の新興株を対象に、代替可能性（置き換えられにくさ）をスコアリングするCLIアプリです。  
オンデマンド実行とデイリー自動実行の両方に対応しています。

## 技術スタック

- Python 3.11+
- Click（CLI）
- yfinance（株価・財務データ取得）
- pandas（データ処理）
- schedule（デイリー実行）
- PyYAML（設定管理）

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 設定

`config.yaml` で条件を設定します。

- `screening.tickers`: 銘柄リスト上書き（空なら Energy セクター取得を試行）
- `screening.market_cap_min` / `market_cap_max`: 時価総額レンジ
- `scoring.weights`: 各評価観点の重み
- `scoring.market_concentration_penalty_per_peer` / `sector_diversity_penalty_per_peer`: 同テーマ銘柄数に対する減点幅
- `report`: 既定出力設定
- `schedule`: デイリー実行時刻と出力先

## 使い方

### オンデマンドスクリーニング

```bash
python -m src.cli run
python -m src.cli run --output csv
python -m src.cli run --output csv --csv-path out/result.csv
```

### デイリー自動実行

```bash
python scheduler/daily_runner.py
```

## スコアリング観点（初期実装）

- 市場集中度（同テーマ銘柄数が少ないほど高評価）
- 財務指標（時価総額レンジ、売上成長率、利益率）
- 株価モメンタム（価格トレンド、ボラティリティ）
- セクター多様性（テーマの希少性）

スコアは 0〜100 に正規化され、`substitutability_score` として出力されます。

## テスト

```bash
python -m unittest discover -q
```
