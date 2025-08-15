import os
import pandas as pd
from sqlalchemy import text

# 移動平均計算関数
def calculate_moving_average(data, window=30):
    return data.rolling(window=window).mean()

# ゴールデンクロス/デッドクロス計算関数
def calculate_crosses(df):
    short_window = int(os.getenv('GOLDEN_DEAD_SHORT_WINDOW', 25))
    long_window = int(os.getenv('GOLDEN_DEAD_LONG_WINDOW', 75))
    df = df.copy()
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    golden_cross = (df['short_ma'] > df['long_ma']) & (df['short_ma'].shift(1) <= df['long_ma'].shift(1))
    dead_cross = (df['short_ma'] < df['long_ma']) & (df['short_ma'].shift(1) >= df['long_ma'].shift(1))
    return golden_cross, dead_cross

# RSI計算関数
def calculate_rsi(df):
    window = int(os.getenv('RSI_WINDOW', 14))
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD計算関数
def calculate_macd(df):
    fast = int(os.getenv('MACD_FAST', 12))
    slow = int(os.getenv('MACD_SLOW', 26))
    signal = int(os.getenv('MACD_SIGNAL', 9))
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# 指標計算とDB保存
def calculate_indicators(df):
    """DataFrameに対してテクニカル指標を一括計算"""
    df = df.copy()
    # クロス指標計算
    df['golden_cross'], df['dead_cross'] = calculate_crosses(df)
    # RSI計算
    df['rsi'] = calculate_rsi(df)
    # MACD計算
    df['macd'], df['signal_line'] = calculate_macd(df)
    return df[['symbol', 'date', 'golden_cross', 'dead_cross', 'rsi', 'macd', 'signal_line']]

def batch_store_indicators(df, engine):
    """DataFrameの内容をバッチでUPSERT"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO technical_indicators 
                (symbol, date, golden_cross, dead_cross, rsi, macd, signal_line)
                VALUES 
                (:symbol, :date, :golden_cross, :dead_cross, :rsi, :macd, :signal_line)
                ON CONFLICT (symbol, date) DO UPDATE SET
                    golden_cross = EXCLUDED.golden_cross,
                    dead_cross = EXCLUDED.dead_cross,
                    rsi = EXCLUDED.rsi,
                    macd = EXCLUDED.macd,
                    signal_line = EXCLUDED.signal_line
            """), df.to_dict('records'))
        return True
    except Exception as e:
        print(f"バッチ保存エラー: {str(e)}")
        return False
