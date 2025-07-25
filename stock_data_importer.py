import yfinance as yf
import psycopg2
import pandas as pd
from datetime import datetime
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
    stock = yf.Ticker(ticker)
    
    # 過去1年間の日次データを取得
    hist = stock.history(period="1y")
    
    # データベースに挿入
    for index, row in hist.iterrows():
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

# 変更をコミット
conn.commit()
print("データ保存完了")

# データベース接続を閉じる
conn.close()
