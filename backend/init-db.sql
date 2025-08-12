-- ユーザーにデータベースの全権限を付与
GRANT ALL PRIVILEGES ON DATABASE stock_analyzer TO stock_user;

-- 拡張機能の有効化（必要に応じて）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 銘柄情報テーブルの作成
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    market_category TEXT,
    industry_code_33 TEXT,
    industry_name_33 TEXT,
    industry_code_17 TEXT,
    industry_name_17 TEXT,
    scale_code TEXT,
    scale_name TEXT,
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

-- 推奨セッションテーブルの作成
CREATE TABLE IF NOT EXISTS recommendation_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    principal DECIMAL(20,4) NOT NULL,
    risk_tolerance VARCHAR(20) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    symbols TEXT[] NOT NULL,
    technical_filter TEXT
);

-- 推奨結果テーブルの作成
CREATE TABLE IF NOT EXISTS recommendation_results (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES recommendation_sessions(session_id),
    symbol TEXT NOT NULL REFERENCES stocks(symbol),
    name TEXT NOT NULL,
    allocation TEXT NOT NULL,
    confidence DECIMAL(5,4),
    reason TEXT,
    target_price DECIMAL(20,4),
    rating VARCHAR(20)
);
