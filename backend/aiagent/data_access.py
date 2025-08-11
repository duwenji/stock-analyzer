import pandas as pd
from typing import List, Dict
from utils import get_db_engine, setup_backend_logger

logger = setup_backend_logger(__name__)

def fetch_company_infos(symbols: List[str]) -> str:
    """銘柄情報をCSV形式で取得"""
    if not symbols:
        return ""
    
    valid_symbols = [s for s in symbols if s and isinstance(s, str)]
    if not valid_symbols:
        return ""
        
    query = f"""
        SELECT symbol, name, industry_name_33, industry_name_17
        FROM stocks
        WHERE symbol IN ({','.join([f"'{s}'" for s in valid_symbols])})
    """
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    result = []
    for _, row in df.iterrows():
        result.append(f"{row['symbol']}:")
        result.append(pd.DataFrame([row]).drop(columns=['symbol']).to_csv(index=False))
    
    return "\n".join(result)

async def fetch_news(symbols: List[str]) -> List[Dict]:
    """symbolsを基に関連ニュースを取得（モック実装）"""
    if not symbols:
        return [{
            "title": "市場ニュース", 
            "summary": "本日の株式市場は概ね好調です",
            "source": "日経新聞"
        }]
    
    valid_symbols = [s for s in symbols if s and isinstance(s, str)]
    if not valid_symbols:
        return [{
            "title": "市場ニュース", 
            "summary": "本日の株式市場は概ね好調です",
            "source": "日経新聞"
        }]
        
    query = f"""
        SELECT symbol, name, industry_name_33, industry_name_17
        FROM stocks
        WHERE symbol IN ({','.join([f"'{s}'" for s in valid_symbols])})
    """
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return [{
            "title": "市場ニュース", 
            "summary": "本日の株式市場は概ね好調です",
            "source": "日経新聞"
        }]
    
    first_company = df.iloc[0]
    return [{
        "title": f"{first_company['name']}に関するニュース",
        "summary": f"{first_company['industry_name_33']}業界の{first_company['name']}が好調",
        "source": "仮想ニュースソース"
    }]

def fetch_technical_indicators(symbols: List[str], limit: int = 10) -> str:
    """テクニカル指標を銘柄ごとにCSV形式で取得"""
    if not symbols:
        return ""
        
    query = f"""
        SELECT DISTINCT ON (symbol)
        symbol, to_char(date, 'YYYY/MM/DD') as date, 
        golden_cross, dead_cross, rsi, macd, signal_line 
        FROM technical_indicators
        WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
        ORDER BY symbol, date DESC
        LIMIT {limit}
    """
    logger.debug(query)
    
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    result = []
    for symbol, group in df.groupby('symbol'):
        result.append(f"{symbol}:")
        result.append(group.drop(columns=['symbol']).to_csv(index=False))
    
    return "\n".join(result)

def fetch_price_history(symbols: List[str], limit: int = 90) -> str:
    """株価履歴を銘柄ごとにCSV形式で取得（過去3ヶ月分）"""
    if not symbols:
        return ""
        
    query = f"""
        SELECT symbol, to_char(date, 'YYYY/MM/DD') as date, open, high, low, close, volume 
        FROM stock_prices
        WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
          AND date >= current_date - interval '1 months'
        ORDER BY symbol, date DESC
    """
    logger.debug(query)
    
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    result = []
    for symbol, group in df.groupby('symbol'):
        result.append(f"{symbol}:")
        result.append(group.drop(columns=['symbol']).to_csv(index=False))
    
    return "\n".join(result)
