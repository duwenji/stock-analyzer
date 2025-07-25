import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from sqlalchemy import create_engine, text
from matplotlib.font_manager import FontProperties
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET  # XML処理用

# 環境変数の読み込み
load_dotenv()

# 日本語フォント設定（Windows用）
font_prop = FontProperties(fname=r'C:\Windows\Fonts\msgothic.ttc', size=9)
title_font = FontProperties(fname=r'C:\Windows\Fonts\msgothic.ttc', size=12)

# SQLAlchemyエンジンの作成
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"
)

# 株価データの読み込み（ローソク足用に全データ取得）
df = pd.read_sql_query("""
    SELECT symbol, date, open, high, low, close, volume
    FROM stock_prices
    ORDER BY date
""", engine, parse_dates=['date'])

# タイムスタンプ列をdatetime型に変換（PostgreSQLからは通常datetimeオブジェクトで取得される）
# 必要に応じてタイムゾーンを設定
df['date'] = pd.to_datetime(df['date'])

#print("株価データ:", df.dtypes)
#
## タイムゾーン情報を削除（ナイーブなdatetimeにする）
#df['date'] = df['date'].dt.tz_localize(None)
#
## デバッグ: 変換後の日付データを出力
#print("\nUTC変換後の日付データサンプル:")
#print(df['date'].head())

# 銘柄情報の読み込み
company_names_df = pd.read_sql_query("""
    SELECT symbol, name 
    FROM stocks
""", engine)
company_names = dict(zip(company_names_df['symbol'], company_names_df['name']))

# 移動平均計算関数
def calculate_moving_average(data, window=30):
    return data.rolling(window=window).mean()

# ゴールデンクロス/デッドクロス計算関数
def calculate_crosses(df, short_window=25, long_window=75):
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    golden_cross = (df['short_ma'] > df['long_ma']) & (df['short_ma'].shift(1) <= df['long_ma'].shift(1))
    dead_cross = (df['short_ma'] < df['long_ma']) & (df['short_ma'].shift(1) >= df['long_ma'].shift(1))
    return pd.DataFrame({'golden_cross': golden_cross, 'dead_cross': dead_cross})

# RSI計算関数
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return pd.DataFrame({'rsi': rsi})

# MACD計算関数
def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({'macd': macd, 'signal_line': signal_line})

# 銘柄ごとにXML分析レポートを生成
report_path = 'reports/stock_analysis.xml'
os.makedirs('reports', exist_ok=True)

symbols = df['symbol'].unique()

# ファイルをオープンし、少しずつ書き込み
os.makedirs('reports', exist_ok=True)
with open(report_path, 'w', encoding='utf-8') as f:
    # XML宣言とルート要素の開始タグ
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write('<StockAnalysisReport>\n')
    
    for symbol in symbols:
        try:
            symbol_df = df[df['symbol'] == symbol].copy()
            symbol_df.set_index('date', inplace=True)
            
            # 移動平均計算
            symbol_df['MA30'] = calculate_moving_average(symbol_df['close'])
            
            # テクニカル指標計算
            crosses = calculate_crosses(symbol_df).add_prefix('cross_')
            rsi = calculate_rsi(symbol_df).add_prefix('rsi_')
            macd_data = calculate_macd(symbol_df).add_prefix('macd_')
            
            # 結果を結合
            symbol_df = pd.concat([symbol_df, crosses, rsi, macd_data], axis=1)
            symbol_df.rename(columns={
                'cross_golden_cross': 'golden_cross',
                'cross_dead_cross': 'dead_cross',
                'rsi_rsi': 'rsi',
                'macd_macd': 'macd',
                'macd_signal_line': 'signal_line'
            }, inplace=True)
            
            # テクニカル指標をデータベースに保存
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM technical_indicators WHERE symbol = :symbol"), {'symbol': symbol})
                conn.commit()
                
                for idx, row in symbol_df.iterrows():
                    golden_cross_val = row['golden_cross'].item() if hasattr(row['golden_cross'], 'item') else row['golden_cross']
                    dead_cross_val = row['dead_cross'].item() if hasattr(row['dead_cross'], 'item') else row['dead_cross']
                    rsi_val = row['rsi'].item() if hasattr(row['rsi'], 'item') else row['rsi']
                    macd_val = row['macd'].item() if hasattr(row['macd'], 'item') else row['macd']
                    signal_line_val = row['signal_line'].item() if hasattr(row['signal_line'], 'item') else row['signal_line']
                    
                    insert_query = text("""
                        INSERT INTO technical_indicators (symbol, date, golden_cross, dead_cross, rsi, macd, signal_line)
                        VALUES (:symbol, :date, :golden_cross, :dead_cross, :rsi, :macd, :signal_line)
                    """)
                    params = {
                        'symbol': symbol,
                        'date': idx,
                        'golden_cross': golden_cross_val,
                        'dead_cross': dead_cross_val,
                        'rsi': rsi_val,
                        'macd': macd_val,
                        'signal_line': signal_line_val
                    }
                    conn.execute(insert_query, params)
                conn.commit()
        
        except Exception as e:
            print(f"エラーが発生したため銘柄 {symbol} をスキップします: {str(e)}")
            continue
        
        # ローソク足チャートの作成
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        plot_df = symbol_df[['open', 'high', 'low', 'close', 'volume']].copy()
        plot_df.columns = ['Open','High','Low','Close','Volume']
        utc_dates = symbol_df.index
        dates = mdates.date2num(utc_dates.to_pydatetime())
        plot_df.index = utc_dates
        
        ohlc_data = []
        for i, (date, row) in enumerate(plot_df.iterrows()):
            ohlc_data.append((
                mdates.date2num(date),
                row['Open'],
                row['High'],
                row['Low'],
                row['Close']
            ))
        
        candlestick_ohlc(ax1, ohlc_data, width=0.6, colorup='r', colordown='g', alpha=1.0)
        ax1.plot([d[0] for d in ohlc_data], symbol_df['MA30'], label='30日移動平均', color='blue')
        ax1.set_title(f'{company_names.get(symbol, "")} ({symbol}) ローソク足チャート', fontproperties=title_font)
        ax1.set_ylabel('価格', fontproperties=font_prop)
        ax1.legend(prop=font_prop)
        
        ax2.bar(dates, symbol_df['volume'], color='gray')
        ax2.set_xlabel('日付', fontproperties=font_prop)
        
        for ax in [ax1, ax2]:
            ax.xaxis_date()
            locator = mdates.AutoDateLocator()
            formatter = mdates.AutoDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            for label in ax.get_xticklabels():
                label.set_fontproperties(font_prop)

        plt.tight_layout()
        plt.savefig(os.path.abspath(f'reports/{symbol}_candle_chart.png'))
        plt.close()
        
        # XML要素の作成
        stock_elem = ET.Element("Stock")
        stock_elem.set("symbol", symbol)
        stock_elem.set("name", company_names.get(symbol, ""))
        
        ET.SubElement(stock_elem, "ChartImage").text = f'reports/{symbol}_candle_chart.png'
        
        indicators_elem = ET.SubElement(stock_elem, "Indicators")
        ET.SubElement(indicators_elem, "Close").text = f"{symbol_df['close'].iloc[-1]:.2f}"
        ET.SubElement(indicators_elem, "MA30").text = f"{symbol_df['MA30'].iloc[-1]:.2f}"
        ET.SubElement(indicators_elem, "Volume").text = f"{symbol_df['volume'].iloc[-1]:,}"
        ET.SubElement(indicators_elem, "PriceRange").text = f"{symbol_df['high'].iloc[-1] - symbol_df['low'].iloc[-1]:.2f}"
        
        rsi_elem = ET.SubElement(indicators_elem, "RSI")
        rsi_elem.set("value", f"{symbol_df['rsi'].iloc[-1]:.2f}")
        rsi_state = '買われすぎ' if symbol_df['rsi'].iloc[-1] > 70 else '売られすぎ' if symbol_df['rsi'].iloc[-1] < 30 else '中立'
        rsi_elem.set("state", rsi_state)
        
        macd_elem = ET.SubElement(indicators_elem, "MACD")
        macd_elem.set("value", f"{symbol_df['macd'].iloc[-1]:.4f}")
        macd_elem.set("signal", f"{symbol_df['signal_line'].iloc[-1]:.4f}")
        macd_trend = '強気' if symbol_df['macd'].iloc[-1] > symbol_df['signal_line'].iloc[-1] else '弱気'
        macd_elem.set("trend", macd_trend)
        
        ET.SubElement(indicators_elem, "GoldenCross").text = '有' if symbol_df['golden_cross'].iloc[-1] else '無'
        ET.SubElement(indicators_elem, "DeadCross").text = '有' if symbol_df['dead_cross'].iloc[-1] else '無'
        
        # XML要素をファイルに書き込み
        stock_xml = ET.tostring(stock_elem, encoding='unicode')
        f.write(f"  {stock_xml}\n")
        f.flush()
    
    # ルート要素の終了タグ
    f.write('</StockAnalysisReport>')

# エンジンを閉じる
engine.dispose()

print(f"株式分析レポートを生成しました: {report_path}")
