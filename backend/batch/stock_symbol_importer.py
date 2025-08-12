import psycopg2
import os
import pandas as pd
import requests
from io import BytesIO

# プロジェクトルートをsys.pathに追加
from utils import initialize_environment

# 環境初期化
initialize_environment()

# JPXから全上場銘柄リストを取得（正しいURL使用）
def fetch_jpx_tickers():
    url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
    response = requests.get(url)
    
    # Excelをデータフレームに読み込み
    df = pd.read_excel(BytesIO(response.content))   
    # 必要な列を選択（最新の列名に基づく）
    required_columns = ['コード', '銘柄名', '市場・商品区分', '33業種コード', 
                       '33業種区分', '17業種コード', '17業種区分', '規模コード', '規模区分']
    df = df[required_columns]
    
    # ティッカーシンボルを生成（コードに'.T'を追加）
    df['ticker'] = df['コード'].astype(str) + '.T'
    return df

# 全日本株銘柄を取得
jpx_df = fetch_jpx_tickers()
print(f"JPXから {len(jpx_df)} 件の銘柄情報を取得しました")

# PostgreSQLデータベースに接続
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# 100件ごとにバッチ処理
batch_size = 100
total_rows = len(jpx_df)
for i in range(0, total_rows, batch_size):
    batch = jpx_df.iloc[i:i+batch_size]
    print(f"処理中: {i+1}-{min(i+batch_size, total_rows)}/{total_rows}件")
    
    # バッチデータをタプルのリストに変換
    data = [(
        row['ticker'],
        str(row['コード']),
        row['銘柄名'],
        row['市場・商品区分'],
        row['33業種コード'],
        row['33業種区分'],
        row['17業種コード'],
        row['17業種区分'],
        row['規模コード'],
        row['規模区分']
    ) for _, row in batch.iterrows()]
    
    # バッチ挿入
    try:
        cursor.executemany('''
            INSERT INTO stocks (
                symbol, code, name, market_category, 
                industry_code_33, industry_name_33,
                industry_code_17, industry_name_17,
                scale_code, scale_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE
            SET 
                code = EXCLUDED.code,
                name = EXCLUDED.name,
                market_category = EXCLUDED.market_category,
                industry_code_33 = EXCLUDED.industry_code_33,
                industry_name_33 = EXCLUDED.industry_name_33,
                industry_code_17 = EXCLUDED.industry_code_17,
                industry_name_17 = EXCLUDED.industry_name_17,
                scale_code = EXCLUDED.scale_code,
                scale_name = EXCLUDED.scale_name
        ''', data)
        conn.commit()
        print(f"  {len(data)}件を保存しました")
    except Exception as e:
        conn.rollback()
        print(f"  バッチ{i+1}-{i+len(data)}の保存中にエラー: {str(e)}")
        # 失敗したバッチを1件ずつ処理
        for _, row in batch.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO stocks (
                        symbol, code, name, market_category, 
                        industry_code_33, industry_name_33,
                        industry_code_17, industry_name_17,
                        scale_code, scale_name
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE
                    SET 
                        code = EXCLUDED.code,
                        name = EXCLUDED.name,
                        market_category = EXCLUDED.market_category,
                        industry_code_33 = EXCLUDED.industry_code_33,
                        industry_name_33 = EXCLUDED.industry_name_33,
                        industry_code_17 = EXCLUDED.industry_code_17,
                        industry_name_17 = EXCLUDED.industry_name_17,
                        scale_code = EXCLUDED.scale_code,
                        scale_name = EXCLUDED.scale_name
                ''', (
                    row['ticker'],
                    str(row['コード']),
                    row['銘柄名'],
                    row['市場・商品区分'],
                    row['33業種コード'],
                    row['33業種区分'],
                    row['17業種コード'],
                    row['17業種区分'],
                    row['規模コード'],
                    row['規模区分']
                ))
                conn.commit()
                print(f"    {row['ticker']} を保存しました")
            except Exception as e2:
                print(f"    {row['ticker']} の保存中にエラー: {str(e2)}")

# 変更をコミット
conn.commit()
print("銘柄情報の保存完了")

# データベース接続を閉じる
cursor.close()
conn.close()
