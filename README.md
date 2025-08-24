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

### 方法1: Dockerを使用した実行（推奨）
#### 前提条件
- DockerとDocker Composeがインストールされていること

#### Linux/Mac環境での手順
1. 環境変数ファイルの設定:
```bash
# backend/.env.docker ファイルを編集して実際の値を設定
cp backend/.env.example backend/.env.docker
# エディタで backend/.env.docker を開き、DEEPSEEK_API_KEYなどを設定
```

2. Docker環境の起動:
```bash
# 実行権限の付与
chmod +x run-docker.sh

# Docker環境の起動
./run-docker.sh
```

#### Windows環境での手順
1. 環境変数ファイルの設定:
```cmd
:: backend\.env.docker ファイルを編集して実際の値を設定
copy backend\.env.example backend\.env.docker
:: エディタで backend\.env.docker を開き、DEEPSEEK_API_KEYなどを設定
```

2. Docker環境の起動:
```cmd
run-docker.bat
```

3. アプリケーションへのアクセス:
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- データベース: localhost:5432

#### 管理コマンド
```bash
# Linux/Mac
cd backend && docker-compose logs -f
cd backend && docker-compose down
cd backend && docker-compose restart

# Windows
cd backend && docker-compose logs -f
cd backend && docker-compose down  
cd backend && docker-compose restart
```

### 方法2: 手動インストール
#### バックエンド
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

#### フロントエンド
```bash
cd frontend
npm install
```

## 実行方法
### Dockerを使用する場合
```bash
./run-docker.sh
```

### 手動で実行する場合
#### バックエンド（APIサーバー）
```bash
cd backend
python src/api.py
```

#### フロントエンド（Web UI）
```bash
cd frontend
npm start
```

## Docker環境構築詳細

### ディレクトリ構造（Docker関連ファイル追加後）
```
株式分析システム
├── backend/
│   ├── Dockerfile              # バックエンド用Dockerイメージ定義
│   ├── docker-compose.yml      # 全サービス定義（PostgreSQL + バックエンド + フロントエンド）
│   ├── .env.docker            # Docker環境用環境変数設定ファイル
│   └── ...
├── frontend/
│   ├── Dockerfile              # フロントエンド用Dockerイメージ定義
│   └── ...
├── run-docker.sh               # Linux/Mac用自動実行スクリプト
├── run-docker.bat              # Windows用自動実行バッチファイル
└── ...
```

### 各サービスのポート設定
- **フロントエンド**: 3000番ポート
- **バックエンドAPI**: 8000番ポート  
- **PostgreSQL**: 5432番ポート

### 環境変数設定
`backend/.env.docker` ファイルに以下の設定が必要です：
```env
# データベース設定
DB_NAME=stock_analyzer
DB_USER=stock_user
DB_PASSWORD=strong_password

# DeepSeek APIキー（必須）
DEEPSEEK_API_KEY=your_actual_api_key_here

# テクニカル指標設定
SHORT_MA_WINDOW=25
LONG_MA_WINDOW=75
RSI_WINDOW=14
```

### トラブルシューティング

#### 1. ポート競合が発生する場合
既に3000, 8000, 5432ポートを使用している場合は、`docker-compose.yml`のports設定を変更：
```yaml
ports:
  - "3001:3000"    # フロントエンド
  - "8001:8000"    # バックエンド
  - "5433:5432"    # データベース
```

#### 2. ビルドエラーが発生する場合
```bash
# キャッシュを無視して再ビルド
cd backend && docker-compose build --no-cache

# 個別サービスの再ビルド
docker-compose build backend
docker-compose build frontend
```

#### 3. データベース接続エラー
データベースの初期化が完了するまで待機：
```bash
# データベースのログを確認
docker-compose logs postgres

# データベースが準備できているか確認
docker-compose exec postgres pg_isready
```

#### 4. ディスク容量不足
不要なDockerリソースを削除：
```bash
# 未使用のイメージ、コンテナ、ボリュームを削除
docker system prune -a
```

### バックアップとリストア

#### データベースバックアップ
```bash
# 実行中のコンテナからバックアップ
docker-compose exec postgres pg_dump -U stock_user stock_analyzer > backup.sql
```

#### データベースリストア
```bash
# バックアップファイルからリストア
docker-compose exec -T postgres psql -U stock_user stock_analyzer < backup.sql
```

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。
