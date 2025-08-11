# 技術コンテキスト

## 開発環境
- OS: Windows 11/macOS/Linux
- エディタ: Visual Studio Code
- バージョン管理: Git
- Pythonバージョン: 3.10+

## 主要技術スタック
- バックエンド:
  - Python 3.10+
  - FastAPI (REST API)
  - SQLAlchemy (ORM)
  - yfinance (データ取得)
  - pandas (データ処理)
  - matplotlib (可視化)
  
- フロントエンド:
  - React (TypeScript)
  - Axios (API通信)
  - Chart.js (データ可視化)

- データベース:
  - PostgreSQL
  - psycopg2 (接続ライブラリ)

- AI統合:
  - Deepseek API (実装済み)
  - 構造化プロンプトテンプレート
  - Evaluator-Optimizerワークフロー

## 主要ライブラリ
- yfinance: 株価データ取得
- pandas: データ分析と処理
- matplotlib: チャート生成
- psycopg2: データベース管理
- deepseek: Deepseek APIクライアント

## テストツール
- 単体テスト: pytest
- カバレッジ計測: coverage.py
- 静的解析: flake8, mypy

## デプロイメント
- ローカル環境でプロトタイプ実行
- タスクスケジューラによる定期実行（Windowsタスクスケジューラ/cron）

## 環境設定と依存関係管理
- 仮想環境: `venv` を使用
- アクティベート: `.\venv\Scripts\activate` (Windows)
- 依存関係インストール: `pip install -r requirements.txt`
- 依存関係更新: `pip freeze > requirements.txt`
- Windows環境での更新コマンド: `pip install --upgrade pip && pip list --outdated && pip install -U [パッケージ名]`
- サンプルスクリック: `db_sample.py` (データベース接続サンプル)

## 更新済み主要ライブラリバージョン (2025年7月25日更新)
- beautifulsoup4: 4.13.4
- certifi: 2025.7.14
- cffi: 1.17.1
- fonttools: 4.59.0
- matplotlib: 3.10.3
- multitasking: 0.0.12
- numpy: 2.3.2
- pandas: 2.3.1
- psycopg2-binary: 2.9.10
- requests: 2.32.4
- SQLAlchemy: 2.0.41
- yfinance: 0.2.65

## API仕様
### バックエンドAPI (backend/api.py)
- 銘柄一覧取得: GET /stocks
  - パラメータ: page, limit, search, sort_by, sort_order
- AI銘柄推奨: POST /api/recommend
  - パラメータ: principal, risk_tolerance, strategy, symbols
- チャート画像取得: GET /chart/{symbol}

### フロントエンド (frontend/src/App.tsx)
- タブ切り替え: 銘柄一覧 ↔ AI銘柄推奨
- 推奨フォーム: 元本、リスク許容度、戦略を入力
- 推奨結果表示: AIが生成した推奨銘柄を表示

## フロントエンド依存関係の課題

### React 19の互換性問題
- 現在のバージョン: React 19.1.0
- 問題のある依存関係:
  - react-scripts: 5.0.1 (React 19と完全互換ではない)
  - @testing-library/react: 16.3.0 (古いバージョン)
  - その他のテスト関連ライブラリが古いバージョン
- 一時的解決策:
  ```bash
  npm install --legacy-peer-deps
  ```
- 恒久的解決策が必要:
  - 依存関係のバージョンアップグレード
  - またはReactをダウングレード

## コマンド実行ポートフォリオ

### Pythonスクリプト実行
- メインスクリプト実行:
  ```bash
  python technical_indicator_calculator.py
  ```
- テスト実行:
  ```bash
  pytest tests/
  ```

### データベース操作
- PostgreSQLコンソール起動:
  ```bash
  psql -d stock_data
  ```
- バックアップ作成:
  ```bash
  pg_dump -Fc stock_data > backup/stock_data_$(date +%Y%m%d).dump
  ```

### エラーハンドリング
- Pythonスクリプト内での例外処理:
  ```python
  try:
      # リスクのある操作
  except Exception as e:
      logging.error(f"エラー発生: {str(e)}")
