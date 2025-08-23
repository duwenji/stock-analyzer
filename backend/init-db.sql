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
    session_id SERIAL PRIMARY KEY,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    principal DECIMAL(20,4) NOT NULL,
    risk_tolerance VARCHAR(20) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    symbols TEXT[] NOT NULL,
    technical_filter TEXT,
    prompt_id INTEGER REFERENCES prompt_templates(id),
    ai_raw_response TEXT,
    total_return_estimate VARCHAR(20)
);
-- 変更内容の確認クエリ
COMMENT ON COLUMN recommendation_sessions.ai_raw_response IS 'AIからの生のレスポンスデータ（JSON形式など）';
COMMENT ON COLUMN recommendation_sessions.total_return_estimate IS '期待リターン推定値';

-- 推奨結果テーブルの作成
CREATE TABLE IF NOT EXISTS recommendation_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES recommendation_sessions(session_id),
    symbol TEXT NOT NULL REFERENCES stocks(symbol),
    name TEXT NOT NULL,
    allocation TEXT NOT NULL,
    confidence DECIMAL(5,4),
    reason TEXT
);

-- プロンプトテンプレートテーブルの作成
CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    agent_type VARCHAR(20) NOT NULL DEFAULT 'direct',
    system_role TEXT,
    user_template TEXT NOT NULL,
    output_format TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- プロンプトテンプレート初期データ
INSERT INTO prompt_templates (
    name, agent_type, system_role, user_template, output_format
) VALUES 
(
    'deepseek-direct',
    'direct',
    'あなたはプロの株式アナリストです。',
    '### ユーザー情報:\n- 元金: {principal}円\n- リスク許容度: {risk_tolerance}\n- 投資方針: {strategy}\n\n### 利用可能クニカル指標: \n{technical_indicators}\n',
    '{\n  \"recommendations\": [\n    {\n      \"s--Moreymbol\": \"銘柄コード\",\n      \"name\": \"会社名\",\n      \"confidence\": 0-100,\n --More--     \"allocation\": \"推奨割合%\",\n      \"reason\": \"推奨理由\"\n    }\n  ],\n  \"--More--total_return_estimate\": \"期待リターン%\"\n}'
),
(
    '基本推奨プロンプト', 
    'direct',
    'あなたはプロの株式アナリストです。与えられた銘柄情報を基に、投資家向けの推奨を生成してください。',
    '以下の銘柄情報を分析し、投資推奨を生成してください:
    
    銘柄情報:
    {company_infos}
    
    テクニカル指標:
    {technical_indicators}
    
    投資条件:
    元金: {principal}円
    リスク許容度: {risk_tolerance}
    戦略: {strategy}
    
    出力形式に従って回答してください。',
    '{
        "recommendations": [
            {
                "symbol": "銘柄コード",
                "name": "企業名",
                "allocation": "推奨割合(%)",
                "confidence": "信頼度(0-1)",
                "reason": "推奨理由"
            }
        ],
        "summary": "全体の推奨概要"
    }'
),
(
    '詳細分析プロンプト', 
    'direct',
    'あなたはプロの株式アナリストです。銘柄の詳細な分析とリスク評価を行ってください。',
    '以下の銘柄情報を詳細に分析し、リスク評価を含む推奨を生成してください:
    
    銘柄情報:
    {company_infos}
    
    テクニカル指標:
    {technical_indicators}
    
    投資条件:
    元金: {principal}円
    リスク許容度: {risk_tolerance}
    戦略: {strategy}
    
    各銘柄について以下の点を分析してください:
    - 強み
    - 弱み
    - 機会
    - 脅威
    - リスク評価(1-5)',
    '{
        "analysis": [
            {
                "symbol": "銘柄コード",
                "strengths": ["強み1", "強み2"],
                "weaknesses": ["弱み1", "弱み2"],
                "opportunities": ["機会1", "機会2"],
                "threats": ["脅威1", "脅威2"],
                "risk_rating": 3
            }
        ],
        "recommendations": "全体の推奨"
    }'
),
(
    'リスク管理プロンプト', 
    'direct',
    'あなたはリスク管理の専門家です。',
    '以下の銘柄リストから、リスク分散されたポートフォリオを提案してください:
    
    銘柄情報:
    {company_infos}
    
    投資条件:
    元金: {principal}円
    リスク許容度: {risk_tolerance}
    戦略: {strategy}
    
    業種分散とリスク分散を考慮した推奨を生成してください。',
    '{
        "portfolio": [
            {
                "symbol": "銘柄コード",
                "allocation": "割合(%)",
                "sector": "業種",
                "risk_level": "リスクレベル"
            }
        ],
        "diversification": {
            "sectors": ["業種1", "業種2"],
            "risk_distribution": {
                "low": 30,
                "medium": 50,
                "high": 20
            }
        }
    }'
);
