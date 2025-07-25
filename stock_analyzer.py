import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from sqlalchemy import create_engine
from matplotlib.font_manager import FontProperties
import os
from dotenv import load_dotenv

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

# 銘柄ごとに分析
analysis_report = "# 株式分析レポート\n\n"
symbols = df['symbol'].unique()

for symbol in symbols:
    symbol_df = df[df['symbol'] == symbol ].copy()
    symbol_df.set_index('date', inplace=True)
    
    # 移動平均計算
    symbol_df['MA30'] = calculate_moving_average(symbol_df['close'])
    
    # ローソク足チャートの作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # プロット用データの準備（mplfinance用にカラム名を変更）
    plot_df = symbol_df[['open', 'high', 'low', 'close', 'volume']].copy()
    
    # インデックス情報のデバッグ出力（コメントアウト）
    #print(f"\n{symbol} インデックス情報:")
    #print(f"  型: {type(plot_df.index)}")
    #print(f"  範囲: {plot_df.index.min()} ～ {plot_df.index.max()}")
    #print(f"  件数: {len(plot_df.index)}")
    #print(f"  サンプル: {plot_df.index[:5].values}")
    #print("株価データ（plot_df）:", plot_df.dtypes)

    plot_df.columns = ['Open','High','Low','Close','Volume']  # カラム名を大文字に
    
    # UTCタイムゾーンを保持したまま日付処理
    utc_dates = symbol_df.index
    
    # デバッグ出力（コメントアウト）
    #print(f"\n{symbol} UTC日付サンプル:")
    #print(utc_dates[:5])
    
    # 日付をMatplotlib数値形式に変換（タイムゾーン情報付き）
    dates = mdates.date2num(utc_dates.to_pydatetime())
    
    # プロット用にタイムゾーン情報を付加
    plot_df.index = utc_dates
    
    # ローソク足データの準備 (candlestick_ohlc用)
    ohlc_data = []
    for i, (date, row) in enumerate(plot_df.iterrows()):
        ohlc_data.append((
            mdates.date2num(date),
            row['Open'],
            row['High'],
            row['Low'],
            row['Close']
        ))
    
    # candlestick_ohlcを使用したローソク足プロット
    candlestick_ohlc(
        ax1, 
        ohlc_data, 
        width=0.6, 
        colorup='r', 
        colordown='g',
        alpha=1.0
    )
    
    # 移動平均線を追加プロット
    ax1.plot(
        [d[0] for d in ohlc_data], 
        symbol_df['MA30'], 
        label='30日移動平均', 
        color='blue'
    )
    ax1.set_title(f'{company_names.get(symbol, "")} ({symbol}) ローソク足チャート', fontproperties=title_font)
    ax1.set_ylabel('価格', fontproperties=font_prop)
    ax1.legend(prop=font_prop)
    
    # 出来高チャート（変換した日付データを使用）
    ax2.bar(dates, symbol_df['volume'], color='gray')
    ax2.set_xlabel('日付', fontproperties=font_prop)
    # X軸フォーマット設定の最適化
    for ax in [ax1, ax2]:
        # 日付軸設定（タイムゾーンなし）
        ax.xaxis_date()
        locator = mdates.AutoDateLocator()
        formatter = mdates.AutoDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        # 目盛りラベルの回転角度調整
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)

    plt.tight_layout()
    plt.savefig(f'reports/{symbol}_candle_chart.png')
    plt.close()
    
    # 表形式レポートの作成
    analysis_report += f"## {symbol} {company_names.get(symbol, '')} 分析結果\n"
    analysis_report += f"![ローソク足チャート](./reports/{symbol}_candle_chart.png)\n\n"
    analysis_report += "### 主要指標\n"
    analysis_report += "| 指標 | 値 | 状態 |\n"
    analysis_report += "|------|----|------|\n"
    analysis_report += f"| 終値 | {symbol_df['close'].iloc[-1]:.2f} | - |\n"
    analysis_report += f"| 30日移動平均 | {symbol_df['MA30'].iloc[-1]:.2f} | {'上昇' if symbol_df['close'].iloc[-1] > symbol_df['MA30'].iloc[-1] else '下降'} |\n"
    analysis_report += f"| 出来高 | {symbol_df['volume'].iloc[-1]:,} | - |\n"
    analysis_report += f"| 値幅 | {symbol_df['high'].iloc[-1] - symbol_df['low'].iloc[-1]:.2f} | - |\n\n"

# エンジンを閉じる
engine.dispose()

# reportsディレクトリが存在しない場合は作成
os.makedirs('reports', exist_ok=True)

# 分析レポートをファイルに保存
with open('reports/stock_analysis.md', 'w', encoding='utf-8') as f:
    f.write(analysis_report)

print("株式分析レポートを生成しました: stock_analysis.md")
