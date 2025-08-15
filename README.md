# 株式分析システム

## 概要
株式市場データの自動収集と分析を行い、テクニカル指標に基づく投資判断をサポートするシステムです。AIによる銘柄推奨機能と可視化レポートを自動生成します。

## 主な機能
1. **株式データ自動取得** - Yahoo Finance APIからリアルタイム株価データを取得
2. **テクニカル分析** - 移動平均線、RSI、MACDなど主要指標の計算
3. **AI銘柄推奨** - DeepSeek APIを利用した投資戦略提案
4. **レポート自動生成** - Matplotlibによるプロフェッショナルなチャート作成（PNG/PDF形式）
5. **データベース管理** - PostgreSQLによるデータ保存・管理

## 技術スタック
### バックエンド
- Python 3.10+
- 主要ライブラリ: FastAPI, SQLAlchemy, pandas, yfinance, matplotlib, psycopg2
- AI統合: DeepSeek API
- データベース: PostgreSQL

### フロントエンド
- React (TypeScript)
- 主要ライブラリ: React, TypeScript, Axios, Chart.js

## システム構成
```
株式分析システム
├── backend/          # バックエンドスクリプト
│   ├── src/          # ソースコード
│   │   ├── api.py        # FastAPIエンドポイント
│   │   ├── aiagent/      # AI推奨システム
│   │   │   ├── data_access.py
│   │   │   ├── deepseek_direct.py
│   │   │   ├── factory.py
│   │   │   └── interface.py
│   │   ├── batch/        # バッチ処理スクリプト
│   │   │   ├── report_generator.py
│   │   │   ├── stock_data_importer.py
│   │   │   └── technical_indicator_calculator.py
│   │   ├── chart_plotter.py
│   │   ├── models.py
│   │   ├── stock_recommender.py
│   │   ├── technical_indicators.py
│   │   └── utils.py
│   ├── requirements.txt
│   ├── .env.example
│   └── init-db.sql
├── frontend/         # フロントエンド（Reactアプリ）
│   ├── src/
│   │   ├── components/   # Reactコンポーネント
│   │   │   ├── ChartExplanation.tsx
│   │   │   ├── RecommendationConfirmationDialog.tsx
│   │   │   └── SimpleConfirmationDialog.tsx
│   │   ├── PromptManagement.tsx  # プロンプト管理
│   │   ├── RecommendationDetail.tsx
│   │   ├── RecommendationForm.tsx
│   │   ├── RecommendationHistory.tsx
│   │   ├── RecommendationResults.tsx
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── StockList.tsx
│   ├── package.json
│   └── tsconfig.json
├── memory-bank/      # プロジェクトドキュメンテーション
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
DEEPSEEK_API_KEY=your_api_key
```

### フロントエンド
```bash
cd frontend
npm install
```

## 実行方法
### バックエンド（APIサーバー）
```bash
cd backend
python src/api.py
```

### フロントエンド（Web UI）
```bash
cd frontend
npm start
```

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。
