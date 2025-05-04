# Yahoo Finance 株価チャートアプリケーション

このアプリケーションは、Yahoo Financeから株価データを取得し、グラフ表示するWebアプリケーションです。

## 機能

- ユーザーが指定した銘柄の株価データを取得
- 表示期間や足（日足、週足、月足）を設定可能
- デフォルトは直近1年の月足表示
- 取得したデータはSQLiteデータベースに保存
- 2回目以降は前回からの差分のみを取得して表示

## 必要なライブラリ

- yfinance
- pandas
- flask
- flask-cors
- matplotlib
- plotly
- sqlalchemy

## インストール方法

```bash
pip install yfinance pandas flask flask-cors matplotlib plotly sqlalchemy
```

## 使い方

1. アプリケーションを起動

```bash
python run.py
```

2. ブラウザで以下のURLにアクセス

```
http://localhost:51953
```

3. 銘柄コード、足、期間を設定して「取得」ボタンをクリック

## 銘柄コードについて

- 日本株の場合は数字のみでも可能（例: 7203）
- 日本株の場合は自動的に `.T` が追加されます（例: 7203.T）
- 米国株の場合はそのままのシンボルを入力（例: AAPL, MSFT）

## 表示期間

- 1ヶ月（1mo）
- 3ヶ月（3mo）
- 6ヶ月（6mo）
- 1年（1y）
- 2年（2y）
- 5年（5y）
- 10年（10y）
- 全期間（max）

## 足の種類

- 日足（1d）
- 週足（1wk）
- 月足（1mo）

## ファイル構成

- `app.py`: Flaskアプリケーションのメインファイル
- `models.py`: データベースモデル
- `stock_utils.py`: Yahoo Financeからデータを取得するユーティリティ関数
- `init_db.py`: データベースの初期化スクリプト
- `run.py`: アプリケーション起動スクリプト
- `templates/index.html`: フロントエンドのHTMLテンプレート
- `stock_data.db`: SQLiteデータベースファイル（自動生成）

## 注意事項

- Yahoo Financeの利用規約に従って使用してください
- 大量のリクエストを短時間に送ると制限がかかる可能性があります
- このアプリケーションは教育目的で作成されています