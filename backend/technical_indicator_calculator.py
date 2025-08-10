import pandas as pd
import os
import asyncio
import argparse
from datetime import datetime
from utils import get_db_engine, initialize_environment, process_in_symbol_groups
from technical_indicators import calculate_indicators, batch_store_indicators

def format_timedelta(td):
    """経過時間を分:秒形式にフォーマット"""
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}分{seconds}秒"

def show_usage_examples():
    print("""
【使い方】
デフォルト: 全銘柄の最新1日分の指標を計算
  python technical_indicator_calculator.py

特定銘柄の最新5日分を計算:
  python technical_indicator_calculator.py --symbol=7203 --days=5

ヘルプ表示:
  python technical_indicator_calculator.py -h
""")

async def main():
    # 引数解析
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='テクニカル指標計算ツール')
    parser.add_argument('--days', type=int, default=1,
                       help='計算対象の日数（デフォルト:1）')
    parser.add_argument('--symbol', type=str, default=None,
                       help='対象銘柄コード（例: 7203）')
    args = parser.parse_args()

    # 使用例表示
    if not args.symbol and args.days == 1:
        show_usage_examples()
        return
    
    try:
        # 開始時刻記録
        start_time = datetime.now()
        print(f"\n処理開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 環境初期化
        initialize_environment()
        
        # データベースエンジン取得
        engine = get_db_engine()
        
        # 株価データ取得クエリ
        base_query = """
            SELECT symbol, date, open, high, low, close, volume
            FROM stock_prices
            WHERE date >= (
                SELECT MAX(date) - INTERVAL '{} days' 
                FROM stock_prices
            )
        """.format(args.days + 75)

        if args.symbol:
            base_query += f" AND symbol = '{args.symbol}'"
        
        base_query += " ORDER BY symbol, date"
        
        df = pd.read_sql_query(base_query, engine, parse_dates=['date'])
        
        # 日付処理
        df['date'] = pd.to_datetime(df['date'])
        
        # グループサイズ設定
        group_size = 1 if args.symbol else 100
        symbols = df['symbol'].unique()
        total_groups = (len(symbols) // group_size) + 1

        # 進捗表示
        if args.symbol:
            print(f"銘柄 '{args.symbol}' のデータを処理中...")
        else:
            print(f"全{len(symbols)}銘柄を{total_groups}グループに分割して処理...")
        
        processed_symbols = set()
        
        # グループごとに処理
        for i, group_df in enumerate(process_in_symbol_groups(df, group_size), 1):
            try:
                group_symbols = group_df['symbol'].unique()
                elapsed = format_timedelta(datetime.now() - start_time)
                print(f"\nグループ {i}/{total_groups} 処理中 ({len(group_symbols)}銘柄) [経過: {elapsed}]")
                
                # 指標計算
                indicators_df = calculate_indicators(group_df)
                
                # バッチ保存
                if batch_store_indicators(indicators_df, engine):
                    # 処理済み銘柄を記録
                    processed_symbols.update(indicators_df['symbol'].unique())
                    print(f"  {len(group_symbols)}銘柄処理済み、{len(indicators_df)}件指標が格納された。")
                else:
                    print(f" グループ{i}の保存に失敗")
            
            except Exception as e:
                print(f" グループ{i}処理中にエラー: {str(e)}")
                continue
        
        end_time = datetime.now()
        elapsed = format_timedelta(end_time - start_time)
        
        if args.symbol:
            print(f"\n処理完了: 銘柄 '{args.symbol}' のデータを更新")
        else:
            print(f"\n処理完了: {len(processed_symbols)}銘柄のデータを更新")
        
        print(f"開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"総処理時間: {elapsed}")
    
    except Exception as e:
        print(f"致命的エラー: {str(e)}")
    finally:
        # エンジン破棄
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
