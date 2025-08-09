import pandas as pd
import os
import asyncio
from utils import get_db_engine, get_company_names, initialize_environment
from technical_indicators import calculate_and_store, calculate_moving_average

async def main():
    try:
        # 環境初期化
        initialize_environment()
        
        # データベースエンジン取得
        engine = get_db_engine()
        
        # 株価データの読み込み
        df = pd.read_sql_query("""
            SELECT symbol, date, open, high, low, close, volume
            FROM stock_prices
            ORDER BY date
        """, engine, parse_dates=['date'])
        
        # 日付処理
        df['date'] = pd.to_datetime(df['date'])
        
        # 銘柄情報取得
        company_names = get_company_names(engine)
        
        # 銘柄ごとに処理
        symbols = df['symbol'].unique()
        processed_count = 0
        
        for symbol in symbols:
            try:
                print(f"処理中: {symbol} ({company_names.get(symbol, '')})")
                symbol_df = df[df['symbol'] == symbol].copy()
                symbol_df.set_index('date', inplace=True)
                # 移動平均計算
                symbol_df['MA30'] = calculate_moving_average(symbol_df['close'])
        
                # テクニカル指標計算と保存
                if not calculate_and_store(symbol_df, engine):
                    print(f"指標計算失敗: {symbol}")
                    continue
                
                processed_count += 1
                print(f"完了: {symbol}")
            
            except Exception as e:
                print(f"銘柄処理エラー ({symbol}): {str(e)}")
                continue
        
        print(f"\n処理完了: {processed_count}/{len(symbols)}銘柄")
    
    except Exception as e:
        print(f"致命的エラー: {str(e)}")
    finally:
        # エンジン破棄
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
