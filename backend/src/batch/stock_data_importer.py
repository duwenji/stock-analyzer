import yfinance as yf
import psycopg2
import signal
import sys
import pandas as pd
import traceback
from datetime import datetime, timedelta, timezone
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
import logging
import random
from tqdm import tqdm
import jpholiday

# プロジェクトルートをsys.pathに追加
from utils import initialize_environment, setup_backend_logger

# 環境初期化
initialize_environment()
setup_backend_logger()

logger = logging.getLogger(__name__)

# APIレートリミット設定
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))  # デフォルト値を5→2に変更
REQUEST_INTERVAL = float(os.getenv('REQUEST_INTERVAL', 0.5))  # リクエスト間隔(秒)
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))  # 最大リトライ回数

print(f"DB接続情報 (DB_NAME: {os.getenv('DB_NAME')}, DB_USER: {os.getenv('DB_USER')}, DB_PASSWORD: {os.getenv('DB_PASSWORD')})")

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
    pool.closeall()
    exit(1)
logger.info(f"銘柄情報件数: {len(tickers)}")

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

        # 最終取得日が当日または最終取得日以降に営業日がない場合はスキップ
        if last_fetched:
            last_fetched_date = last_fetched.astimezone(jst).date()
            
            # 最終取得日が当日の場合
            if last_fetched_date == today:
                logger.info(f"{ticker} - 本日分のデータを既に取得済みのためスキップ")
                return True
                
            # 最終取得日以降に営業日があるかチェック
            delta = today - last_fetched_date
            has_trading_day = False
            
            # 1日ずつチェック
            for i in range(1, delta.days + 1):
                check_date = last_fetched_date + timedelta(days=i)
                # 土日または祝日でない場合のみ営業日とみなす
                if check_date.weekday() < 5 and not jpholiday.is_holiday(check_date):
                    has_trading_day = True
                    break
            
            if not has_trading_day:
                logger.info(f"{ticker} - 最終取得日({last_fetched_date})以降に営業日がないためスキップ")
                return True

        # データ取得（レートリミット＆リトライ付き）
        retries = 0
        hist = None
        while retries <= MAX_RETRIES:
            try:
                time.sleep(REQUEST_INTERVAL)  # レートリミット
                stock = yf.Ticker(ticker)
                if last_fetched:
                    start_date = (last_fetched + timedelta(days=1)).strftime('%Y-%m-%d')
                    hist = stock.history(start=start_date)
                else:
                    hist = stock.history(period="3y")

                if hist.empty:
                    logger.warning(f"{ticker} - 取得データが空です")

                break  # ループ脱出

            except Exception as e:
                if "Too Many Requests" in str(e) or "429" in str(e):
                    wait_time = (2 ** retries) + random.uniform(0, 1)
                    logger.warning(f"{ticker} - レートリミット検出: {wait_time}秒待機 (リトライ {retries}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    logger.error(f"{ticker} - データ取得エラー: {str(e)}")
                    raise

        if hist is None or hist.empty:
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
        # フルトレースバック情報を取得
        tb_str = traceback.format_exc()
        logger.error(f"{ticker} - 処理中にエラーが発生: {str(e)}\nトレースバック:\n{tb_str}")
        
        # 追加: エラーコンテキスト情報
        logger.error(f"エラー発生時の最終取得日時: {last_fetched}")
        logger.error(f"リトライ回数: {retries}/{MAX_RETRIES}")
        
        return False
    finally:
        cursor.close()
        pool.putconn(conn)

# 進捗表示設定
start_time = time.time()
progress_interval = max(1, len(tickers) // 10)  # 10%間隔

# グローバル中断フラグ
shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    shutdown_flag = True
    print("\n中断シグナルを受信しました。処理を安全に終了します...")
    sys.exit(1)

# シグナルハンドラ登録
signal.signal(signal.SIGINT, signal_handler)

# 並列処理実行
try:
    with tqdm(total=len(tickers), desc="銘柄処理中") as pbar:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for i, ticker in enumerate(tickers):
                logger.info(f"{i}: {ticker}")
                if shutdown_flag:
                    raise KeyboardInterrupt("中断フラグが設定されました")
                    
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

except KeyboardInterrupt:
    print("\n中断リクエストを受信しました。処理を安全に終了します...")
    # スレッドプールのシャットダウン
    executor.shutdown(wait=False)
    # 接続プールのクリーンアップ
    pool.closeall()
    sys.exit(1)
except Exception as e:
    print(f"予期せぬエラーが発生しました: {str(e)}")
    pool.closeall()
    sys.exit(1)
finally:
    pool.closeall()
