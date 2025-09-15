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
    histogram = macd - signal_line
    return macd, signal_line, histogram

# MACDスコア計算関数
def calculate_macd_score(golden_cross, histogram, histogram_prev=None):
    """
    MACDスコアを計算する
    
    Args:
        golden_cross (bool): ゴールデンクロス発生状況
        histogram (float): 現在のMACDヒストグラム値
        histogram_prev (float): 前日のMACDヒストグラム値（オプション）
    
    Returns:
        int: MACDスコア（0-6点）
    """
    score = 0
    
    # ゴールデンクロスで+3点
    if golden_cross:
        score += 3
    
    # ヒストグラムトレンド判定（前日値がある場合）
    if histogram_prev is not None:
        if histogram > histogram_prev:  # ヒストグラム上昇中
            score += 2
    elif histogram > 0:  # 前日値がない場合は単純に正の値で判断
        score += 1
    
    # ヒストグラムが正の値で+1点
    if histogram > 0:
        score += 1
    
    return score

# 指標計算とDB保存
def calculate_indicators(df):
    """DataFrameに対してテクニカル指標を一括計算"""
    df = df.copy()
    # クロス指標計算
    df['golden_cross'], df['dead_cross'] = calculate_crosses(df)
    # RSI計算
    df['rsi'] = calculate_rsi(df)
    # MACD計算（ヒストグラムを含む）
    df['macd'], df['signal_line'], df['histogram'] = calculate_macd(df)
    
    # MACDスコア計算（前日値を使用）
    df['macd_score'] = 0
    for symbol in df['symbol'].unique():
        symbol_mask = df['symbol'] == symbol
        symbol_df = df[symbol_mask].copy()
        
        # 日付でソート
        symbol_df = symbol_df.sort_values('date')
        
        # 各日付に対してMACDスコアを計算
        for i in range(len(symbol_df)):
            current_row = symbol_df.iloc[i]
            golden_cross = current_row['golden_cross']
            histogram = current_row['histogram']
            
            # 前日値がある場合は使用
            histogram_prev = symbol_df.iloc[i-1]['histogram'] if i > 0 else None
            
            # MACDスコア計算
            macd_score = calculate_macd_score(golden_cross, histogram, histogram_prev)
            df.loc[(df['symbol'] == symbol) & (df['date'] == current_row['date']), 'macd_score'] = macd_score
    
    return df[['symbol', 'date', 'golden_cross', 'dead_cross', 'rsi', 'macd', 'signal_line', 'histogram', 'macd_score']]

def batch_store_indicators(df, engine):
    """DataFrameの内容をバッチでUPSERT"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO technical_indicators 
                (symbol, date, golden_cross, dead_cross, rsi, macd, signal_line, histogram, macd_score)
                VALUES 
                (:symbol, :date, :golden_cross, :dead_cross, :rsi, :macd, :signal_line, :histogram, :macd_score)
                ON CONFLICT (symbol, date) DO UPDATE SET
                    golden_cross = EXCLUDED.golden_cross,
                    dead_cross = EXCLUDED.dead_cross,
                    rsi = EXCLUDED.rsi,
                    macd = EXCLUDED.macd,
                    signal_line = EXCLUDED.signal_line,
                    histogram = EXCLUDED.histogram,
                    macd_score = EXCLUDED.macd_score
            """), df.to_dict('records'))
        return True
    except Exception as e:
        print(f"バッチ保存エラー: {str(e)}")
        return False
