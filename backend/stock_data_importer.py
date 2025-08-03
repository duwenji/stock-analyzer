import yfinance as yf
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
import logging
from tqdm import tqdm

from utils import initialize_environment

# 環境初期化
initialize_environment()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 並列処理設定
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))

print(f"DB_NAME: {os.getenv('DB_NAME')}, DB_USER: {os.getenv('DB_USER')}, DB_PASSWORD: {os.getenv('DB_PASSWORD')}")

# 接続プール初期化
pool = ThreadedConnectionPool(
    minconn=1,
    maxconn=MAX_WORKERS,
    host="localhost",
    port=5432,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# 初期接続（テーブル変更用）
conn = pool.getconn()
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
cursor = conn.cursor()

# stocksテーブルに最終取得日時カラムを追加（存在しない場合）
cursor.execute("""
    ALTER TABLE stocks 
    ADD COLUMN IF NOT EXISTS last_fetched TIMESTAMP WITH TIME ZONE
""")

# 銘柄シンボルをデータベースから取得
cursor.execute("SELECT symbol FROM stocks")
tickers = [row[0] for row in cursor.fetchall()]

if not tickers:
    print("データベースに銘柄情報がありません")
    conn.close()
    exit(1)

pool.putconn(conn)

def process_ticker(ticker, pool):
    """個別銘柄のデータ取得・保存処理"""
    conn = pool.getconn()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
    try:
        cursor = conn.cursor()
        
        # 最終取得日時を取得
        cursor.execute("SELECT last_fetched FROM stocks WHERE symbol = %s", (ticker,))
        last_fetched_row = cursor.fetchone()
        last_fetched = last_fetched_row[0] if last_fetched_row else None

        # 日本時間のタイムゾーンを定義
        jst = timezone(timedelta(hours=9))
        today = datetime.now(jst).date()

        # 最終取得日が当日の場合はスキップ
        if last_fetched:
            last_fetched_date = last_fetched.astimezone(jst).date()
            if last_fetched_date == today:
                logger.info(f"{ticker} - 本日分のデータを既に取得済みのためスキップ")
                return True

        # データ取得
        stock = yf.Ticker(ticker)
        if last_fetched:
            start_date = (last_fetched + timedelta(days=1)).strftime('%Y-%m-%d')
            hist = stock.history(start=start_date)
        else:
            hist = stock.history(period="3y")

        if hist.empty:
            logger.warning(f"{ticker} - 取得データが空です")
            return False

        # バルクインサート用データ準備
        data = []
        current_fetch_date = None
        for index, row in hist.iterrows():
            current_fetch_date = index.to_pydatetime().replace(tzinfo=None)
            data.append((
                ticker,
                current_fetch_date,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume'])
            ))

        # バルクインサート実行
        execute_values(cursor,
            """INSERT INTO stock_prices 
               (symbol, date, open, high, low, close, volume)
               VALUES %s
               ON CONFLICT (symbol, date) DO NOTHING""",
            data
        )

        # 最終取得日時を更新
        cursor.execute("""
            UPDATE stocks 
            SET last_fetched = %s 
            WHERE symbol = %s
        """, (current_fetch_date, ticker))

        # 変更をコミット
        conn.commit()
        return True

    except Exception as e:
        logger.error(f"{ticker} - 処理中にエラーが発生: {str(e)}")
        return False
    finally:
        cursor.close()
        pool.putconn(conn)

# 進捗表示設定
start_time = time.time()
progress_interval = max(1, len(tickers) // 10)  # 10%間隔

# 並列処理実行
with tqdm(total=len(tickers), desc="銘柄処理中") as pbar:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i, ticker in enumerate(tickers):
            futures.append(executor.submit(process_ticker, ticker, pool))
            
            # 進捗表示更新
            if (i + 1) % progress_interval == 0 or (i + 1) == len(tickers):
                elapsed = time.time() - start_time
                remaining = (elapsed / (i + 1)) * (len(tickers) - (i + 1))
                logger.info(
                    f"進捗: {i + 1}/{len(tickers)} 銘柄 ({((i + 1)/len(tickers))*100:.1f}%) "
                    f"経過時間: {timedelta(seconds=int(elapsed))} "
                    f"推定残り時間: {timedelta(seconds=int(remaining))}"
                )
            pbar.update(1)

        # 結果確認
        success_count = 0
        for future in as_completed(futures):
            if future.result():
                success_count += 1
            pbar.update(1)

    total_time = time.time() - start_time
    logger.info(
        f"処理完了: {success_count}/{len(tickers)} 銘柄の更新に成功 "
        f"(総処理時間: {timedelta(seconds=int(total_time))}, "
        f"平均: {total_time/len(tickers):.2f}秒/銘柄)"
    )

pool.closeall()
