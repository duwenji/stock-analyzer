import argparse
import pandas as pd
import os
from utils import get_db_engine, get_company_names
from technical_indicators import calculate_and_store, calculate_moving_average
from chart_plotter import plot_candlestick
from report_generator import init_xml_report, finalize_xml_report, generate_stock_entry

def main():
    try:
        # 引数解析
        parser = argparse.ArgumentParser(description='株価分析ツール')
        parser.add_argument('--plot-charts', action='store_true', help='チャートを描画する')
        args = parser.parse_args()

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
        
        # レポートパス設定
        report_path = 'reports/stock_analysis.xml'
        
        # XMLレポート初期化
        if not init_xml_report(report_path):
            raise RuntimeError("XMLレポートの初期化に失敗しました")
        
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
                
                # チャート描画（オプション）
                chart_path = None
                if args.plot_charts:
                    chart_path = plot_candlestick(
                        symbol_df, 
                        symbol, 
                        company_names.get(symbol, ""),
                        output_dir='reports'
                    )
                    if not chart_path:
                        print(f"チャート作成失敗: {symbol}")
                        # チャート作成に失敗しても処理は続行（指標は計算済み）
                
                # XMLエントリー生成
                xml_entry = generate_stock_entry(
                    symbol_df, 
                    symbol, 
                    company_names.get(symbol, ""),
                    chart_path
                )
                
                if not xml_entry:
                    print(f"XML生成失敗: {symbol}")
                    continue
                
                # XMLエントリー書き込み
                with open(report_path, 'a', encoding='utf-8') as f:
                    f.write(f"  {xml_entry}\n")
                
                processed_count += 1
                print(f"完了: {symbol}")
            
            except Exception as e:
                print(f"銘柄処理エラー ({symbol}): {str(e)}")
                continue
        
        # XMLレポート終了処理
        if not finalize_xml_report(report_path):
            raise RuntimeError("XMLレポートの終了処理に失敗しました")
        
        print(f"\n処理完了: {processed_count}/{len(symbols)}銘柄")
        print(f"レポート生成先: {os.path.abspath(report_path)}")
    
    except Exception as e:
        print(f"致命的エラー: {str(e)}")
    finally:
        # エンジン破棄
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    main()
