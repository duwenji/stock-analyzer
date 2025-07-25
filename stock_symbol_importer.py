import yfinance as yf
import psycopg2
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 対象銘柄リスト（トヨタ、ソニー、任天堂）
tickers = ['7203.T', '6758.T', '7974.T']

# PostgreSQLデータベースに接続
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# 各銘柄の情報を取得して保存
for ticker in tickers:
    print(f"処理中: {ticker}")
    stock = yf.Ticker(ticker)
    
    # 企業情報を取得
    info = stock.info
    name = info.get('longName', '')
    industry = info.get('industry', '')
    
    # データベースに挿入
    try:
        cursor.execute('''
            INSERT INTO stocks (symbol, name, industry)
            VALUES (%s, %s, %s)
            ON CONFLICT (symbol) DO NOTHING
        ''', (ticker, name, industry))
        print(f"  {ticker} を保存しました")
    except Exception as e:
        print(f"  {ticker} の保存中にエラー: {str(e)}")

# 変更をコミット
conn.commit()
print("銘柄情報の保存完了")

# データベース接続を閉じる
cursor.close()
conn.close()
