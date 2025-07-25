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
    UNIQUE (symbol, date) -- シンボルと日付の組み合わせをユニークに
);
