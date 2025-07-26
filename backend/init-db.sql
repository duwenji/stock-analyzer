-- ユーザーにデータベースの全権限を付与
GRANT ALL PRIVILEGES ON DATABASE stock_analyzer TO stock_user;

-- 拡張機能の有効化（必要に応じて）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 銘柄情報テーブルの作成
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT,
    industry TEXT,
    last_fetched TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 株価情報テーブルの作成
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, date),
    CONSTRAINT fk_stock_prices_stocks FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

-- テクニカル指標テーブルの作成
CREATE TABLE IF NOT EXISTS technical_indicators (
    symbol TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    golden_cross BOOLEAN,
    dead_cross BOOLEAN,
    rsi DECIMAL(20,4),
    macd DECIMAL(20,4),
    signal_line DECIMAL(20,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);
