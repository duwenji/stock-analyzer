import yfinance as yf
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# PostgreSQLデータベースに接続
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
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

# 各銘柄のデータを取得して保存
for ticker in tickers:
    print(f"取得中: {ticker}")
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
            print(f"{ticker} は本日分のデータを既に取得済みのためスキップします")
            continue


    stock = yf.Ticker(ticker)
        
    # 取得期間の設定
    if last_fetched:
        # 最終取得日時の翌日から現在まで
        start_date = (last_fetched + timedelta(days=1)).strftime('%Y-%m-%d')
        hist = stock.history(start=start_date)
    else:
        # 新規銘柄は過去3年分
        hist = stock.history(period="3y")
    
    # データベースに挿入
    for index, row in hist.iterrows():
        # 最終取得日時を更新（ループ内で直近の日付を保持）
        current_fetch_date = index.to_pydatetime().replace(tzinfo=None)
        
        # print(type(index), index, row)
        cursor.execute('''
            INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO NOTHING
        ''', (
            ticker,
            row.name.strftime('%Y-%m-%d %H:%M:%S%z'),  # インデックスから日付を取得
            float(row['Open']),
            float(row['High']),
            float(row['Low']),
            float(row['Close']),
            int(row['Volume'])
        ))
    
    # 最終取得日時を更新
    if not hist.empty:
        cursor.execute("""
            UPDATE stocks 
            SET last_fetched = %s 
            WHERE symbol = %s
        """, (current_fetch_date, ticker))

    # 変更をコミット
    conn.commit()
    
print("データ保存完了")

# データベース接続を閉じる
conn.close()
