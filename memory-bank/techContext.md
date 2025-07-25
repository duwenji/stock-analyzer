# 技術コンテキスト

## 開発環境
- OS: Windows 11/macOS/Linux
- エディタ: Visual Studio Code
- バージョン管理: Git
- Pythonバージョン: 3.10+

## 主要技術スタック
- プログラミング言語: Python
- データ取得: yfinanceライブラリ
- データ処理: pandas
- 可視化: matplotlib
- データベース: PostgreSQL

## 主要ライブラリ
- yfinance: 株価データ取得
- pandas: データ分析と処理
- matplotlib: チャート生成
- psycopg2: データベース管理

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

## コマンド実行ポートフォリオ

### Pythonスクリプト実行
- メインスクリプト実行:
  ```bash
  python stock_analyzer.py
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
