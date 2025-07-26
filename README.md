# 株式分析システム

## 概要
株式市場データの自動収集と分析を行い、テクニカル指標に基づく投資判断をサポートするシステムです。可視化レポートを自動生成します。

## 主な機能
1. **株式データ自動取得** - Yahoo Finance APIからリアルタイム株価データを取得
2. **テクニカル分析** - 移動平均線、RSIなど主要指標の計算
3. **レポート自動生成** - Matplotlibによるプロフェッショナルなチャート作成（PNG/PDF形式）
4. **データベース管理** - PostgreSQLによるデータ保存・管理

## 技術スタック
### バックエンド
- Python 3.10+
- 主要ライブラリ: pandas, yfinance, matplotlib, psycopg2
- データベース: PostgreSQL

### フロントエンド
- React (TypeScript)
- 主要ライブラリ: React, TypeScript

## システム構成
```
株式分析システム
├── backend/          # バックエンドスクリプト
│   ├── api.py
│   ├── chart_plotter.py
│   ├── stock_analyzer.py
│   ├── stock_data_importer.py
│   ├── technical_indicators.py
│   ├── utils.py
│   ├── requirements.txt
│   ├── .env
│   ├── init-db.sql
│   ├── logs/          # ログファイル
│   └── reports/       # 生成されたレポート
├── frontend/         # フロントエンド（Reactアプリ）
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── StockList.tsx
│   ├── package.json
│   └── tsconfig.json
├── memory-bank/      # プロジェクトドキュメンテーション
├── reports/          # レポート出力ディレクトリ（シンボリックリンク）
└── README.md         # このファイル
```

## インストール方法
### バックエンド
```bash
cd backend
pip install -r requirements.txt
```

1. PostgreSQLデータベースを作成:
```sql
CREATE DATABASE stock_data;
```

2. 環境設定ファイルを作成 (.env):
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data
DB_USER=your_username
DB_PASSWORD=your_password
```

### フロントエンド
```bash
cd frontend
npm install
```

## 実行方法
### バックエンド（データ分析）
```bash
cd backend
python api.py
```

### フロントエンド（Web UI）
```bash
cd frontend
npm start
```

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。
