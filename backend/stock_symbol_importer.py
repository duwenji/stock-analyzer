import yfinance as yf
import psycopg2
import os
import pandas as pd
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# JPXから全上場銘柄リストを取得（正しいURL使用）
def fetch_jpx_tickers():
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    response = requests.get(url)
    
    # Excelをデータフレームに読み込み
    df = pd.read_excel(response.content)
    
    # 必要な列を選択（最新の列名に基づく）
    required_columns = ['コード', '銘柄名', '市場・商品区分']
    df = df[required_columns]
    
    # 上場中銘柄のみフィルタリング（上場廃止日情報がないため全件取得）
    # JPXのリストは上場中銘柄のみを含むためフィルタリング不要
    
    # ティッカーシンボルを生成（コードに'.T'を追加）
    df['ticker'] = df['コード'].astype(str) + '.T'
    return df

# 全日本株銘柄を取得
jpx_df = fetch_jpx_tickers()
print(f"JPXから {len(jpx_df)} 件の銘柄情報を取得しました")

# トヨタ(7203.T)とシャープ(6753.T)を必ず含めつつ、ランダムに100件を選択
required_tickers = ['7203.T', '6753.T']

# 必ず含める銘柄を抽出
required_rows = jpx_df[jpx_df['ticker'].isin(required_tickers)]

# それ以外の銘柄からランダムにサンプリング (100 - 必須銘柄数)
sample_size = 100 - len(required_rows)
other_rows = jpx_df[~jpx_df['ticker'].isin(required_tickers)]

# サンプリング可能な件数が不足する場合の処理
if len(other_rows) < sample_size:
    sample_size = len(other_rows)
    print(f"警告: サンプリング可能な銘柄が不足しています。取得件数: {len(required_rows) + sample_size}件")

sampled_rows = other_rows.sample(n=sample_size, random_state=42)

# 必須銘柄とサンプリング銘柄を結合
jpx_df = pd.concat([required_rows, sampled_rows])
print(f"ランダムサンプリング: 必須銘柄{len(required_rows)}件 + ランダム{sample_size}件 = 合計{len(jpx_df)}件を処理します")

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
for index, row in jpx_df.iterrows():
    ticker = row['ticker']
    jpx_name = row['銘柄名']
    
    print(f"処理中: {ticker} ({jpx_name})")
    stock = yf.Ticker(ticker)
    
    # 企業情報を取得
    info = stock.info
    yf_name = info.get('longName', jpx_name)  # デフォルト値としてJPX銘柄名を使用
    industry = info.get('industry', '')
    
    # データベースに挿入
    try:
        cursor.execute('''
            INSERT INTO stocks (symbol, name, industry)
            VALUES (%s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE
            SET name = EXCLUDED.name,
                industry = EXCLUDED.industry
        ''', (ticker, yf_name, industry))
        print(f"  {ticker} を保存しました")
    except Exception as e:
        print(f"  {ticker} の保存中にエラー: {str(e)}")

# 変更をコミット
conn.commit()
print("銘柄情報の保存完了")

# データベース接続を閉じる
cursor.close()
conn.close()
