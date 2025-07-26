import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# 移動平均計算関数
def calculate_moving_average(data, window=30):
    return data.rolling(window=window).mean()

# ゴールデンクロス/デッドクロス計算関数
def calculate_crosses(df, short_window=25, long_window=75):
    df = df.copy()
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    golden_cross = (df['short_ma'] > df['long_ma']) & (df['short_ma'].shift(1) <= df['long_ma'].shift(1))
    dead_cross = (df['short_ma'] < df['long_ma']) & (df['short_ma'].shift(1) >= df['long_ma'].shift(1))
    return golden_cross, dead_cross

# RSI計算関数
def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# MACD計算関数
def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# 指標計算とDB保存
def calculate_and_store(symbol_df, engine):
    """銘柄データに対してテクニカル指標を計算しデータベースに保存"""
    try:
        # 移動平均計算
        symbol_df['MA30'] = calculate_moving_average(symbol_df['close'])
        
        # クロス指標計算
        golden_cross, dead_cross = calculate_crosses(symbol_df)
        symbol_df['golden_cross'] = golden_cross
        symbol_df['dead_cross'] = dead_cross
        
        # RSI計算
        symbol_df['rsi'] = calculate_rsi(symbol_df)
        
        # MACD計算
        macd, signal_line = calculate_macd(symbol_df)
        symbol_df['macd'] = macd
        symbol_df['signal_line'] = signal_line
        
        # データベース保存処理
        with engine.connect() as conn:
            # 既存データ削除
            conn.execute(text("DELETE FROM technical_indicators WHERE symbol = :symbol"), 
                        {'symbol': symbol_df['symbol'].iloc[0]})
            
            # バルク挿入用データ準備
            records = []
            for idx, row in symbol_df.iterrows():
                records.append({
                    'symbol': row['symbol'],
                    'date': idx,
                    'golden_cross': row['golden_cross'],
                    'dead_cross': row['dead_cross'],
                    'rsi': row['rsi'],
                    'macd': row['macd'],
                    'signal_line': row['signal_line']
                })
            
            # バルク挿入
            if records:
                conn.execute(text("""
                    INSERT INTO technical_indicators 
                    (symbol, date, golden_cross, dead_cross, rsi, macd, signal_line)
                    VALUES 
                    (:symbol, :date, :golden_cross, :dead_cross, :rsi, :macd, :signal_line)
                """), records)
            
            conn.commit()
        return True
    
    except SQLAlchemyError as e:
        print(f"データベース保存エラー: {str(e)}")
        return False
    except Exception as e:
        print(f"指標計算エラー: {str(e)}")
        return False
