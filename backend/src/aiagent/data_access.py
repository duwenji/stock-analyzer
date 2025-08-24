import pandas as pd
from typing import List, Dict
from utils import get_db_engine, setup_backend_logger
from sqlalchemy import select, insert
from models import RecommendationSession, RecommendationResult, PromptTemplate

logger = setup_backend_logger(__name__)

def fetch_company_infos(symbols: List[str]) -> str:
    """銘柄情報を文字列形式で取得"""
    if not symbols:
        return ""
    
    # シンボルを正規化
    normalized_symbols = [normalize_symbol(s) for s in symbols if s and isinstance(s, str)]
    if not normalized_symbols:
        return ""
        
    query = f"""
        SELECT symbol, name, industry_name_33, industry_name_17
        FROM stocks
        WHERE symbol IN ({','.join([f"'{s}'" for s in normalized_symbols])})
    """
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    return df.to_string(header=True, index=False)

async def fetch_news(symbols: List[str]) -> List[Dict]:
    """symbolsを基に関連ニュースを取得（モック実装）"""
    if not symbols:
        return [{
            "title": "市場ニュース", 
            "summary": "本日の株式市場は概ね好調です",
            "source": "日経新聞"
        }]
    
    # シンボルを正規化
    normalized_symbols = [normalize_symbol(s) for s in symbols if s and isinstance(s, str)]
    if not normalized_symbols:
        return [{
            "title": "市場ニュース", 
            "summary": "本日の株式市場は概ね好調です",
            "source": "日経新聞"
        }]
        
    query = f"""
        SELECT symbol, name, industry_name_33, industry_name_17
        FROM stocks
        WHERE symbol IN ({','.join([f"'{s}'" for s in normalized_symbols])})
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

def fetch_technical_indicators(symbols: List[str], limit: int = 100) -> str:
    """テクニカル指標を文字列形式で取得"""
    if not symbols:
        return ""
    
    # シンボルを正規化
    normalized_symbols = [normalize_symbol(s) for s in symbols if s and isinstance(s, str)]
    if not normalized_symbols:
        return ""
        
    query = f"""
        SELECT DISTINCT ON (symbol)
        symbol, to_char(date, 'YYYY/MM/DD') as date, 
        golden_cross, dead_cross, rsi, macd, signal_line 
        FROM technical_indicators
        WHERE symbol IN ({','.join([f"'{s}'" for s in normalized_symbols])})
        ORDER BY symbol, date DESC
        LIMIT {limit}
    """
    #logger.debug(query)
    
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    return df.to_string(header=True, index=False)

def fetch_price_history(symbols: List[str], limit: int = 90) -> str:
    """株価履歴を文字列形式で取得（過去3ヶ月分）"""
    if not symbols:
        return ""
    
    # シンボルを正規化
    normalized_symbols = [normalize_symbol(s) for s in symbols if s and isinstance(s, str)]
    if not normalized_symbols:
        return ""
        
    query = f"""
        SELECT symbol, to_char(date, 'YYYY/MM/DD') as date, open, high, low, close, volume 
        FROM stock_prices
        WHERE symbol IN ({','.join([f"'{s}'" for s in normalized_symbols])})
          AND date >= current_date - interval '1 months'
        ORDER BY symbol, date DESC
    """
    logger.debug(query)
    
    df = pd.read_sql_query(query, get_db_engine())
    if df.empty:
        return ""
    
    return df.to_string(header=True, index=False)

def get_prompt_template(prompt_id: int) -> Dict[str, str]:
    """プロンプトテンプレートをデータベースから取得
    
    Args:
        prompt_id: prompt_templatesテーブルのID
        
    Returns:
        {
            "system_role": システムロールテキスト,
            "user_template": ユーザーテンプレートテキスト,
            "output_format": 出力フォーマット
        }
    """
    try:
        engine = get_db_engine()
        with engine.begin() as conn:
            stmt = select(
                PromptTemplate.system_role,
                PromptTemplate.user_template,
                PromptTemplate.output_format
            ).where(PromptTemplate.id == prompt_id)
            
            result = conn.execute(stmt).fetchone()
            
            if result is None:
                logger.warning(f"指定されたプロンプトテンプレートが見つかりません: prompt_id={prompt_id}")
                return {
                    "system_role": "あなたはプロの株式アナリストです。",
                    "user_template": "以下の銘柄情報を分析して投資推奨を行ってください。\n銘柄情報:\n{company_info}\n\nテクニカル指標:\n{technical_indicators}\n\n価格履歴:\n{price_history}",
                    "output_format": "JSON形式で推奨銘柄とその理由を返してください"
                }
                
            return {
                "system_role": result.system_role or "",
                "user_template": result.user_template,
                "output_format": result.output_format
            }
            
    except Exception as e:
        logger.error(f"プロンプトテンプレートの取得に失敗: {str(e)}")
        raise

def normalize_symbol(symbol: str) -> str:
    """シンボルを正規化（.Tサフィックスを追加）"""
    if symbol and not symbol.endswith('.T'):
        return symbol + '.T'
    return symbol

def save_recommendation(result: Dict, params: Dict, ai_raw_response: str = None) -> bool:
    """推奨結果をデータベースに保存
    
    Args:
        result: パース済みの推奨結果
        params: 推奨パラメータ
        ai_raw_response: AIからの生のレスポンス（オプション）
    """
    try:
        logger.debug(
            f"推奨結果保存開始 - principal: {params['principal']}, "
            f"戦略: {params['strategy']}, "
            f"銘柄数: {len(params['selected_symbols'])}, "
            f"推奨: {result}"
        )
        engine = get_db_engine()
        with engine.begin() as conn:
            # セッション作成
            session_stmt = insert(RecommendationSession).values(
                principal=params['principal'],
                risk_tolerance=params['risk_tolerance'],
                strategy=params['strategy'],
                symbols=params['selected_symbols'],
                technical_filter=params.get('technical_filter'),
                ai_raw_response=ai_raw_response,
                total_return_estimate=result.get('total_return_estimate', -1)
            )
            conn.execute(session_stmt)
            session_id = conn.execute(
                select(RecommendationSession.session_id)
                .order_by(RecommendationSession.session_id.desc())
                .limit(1)
            ).scalar()
            
            # 結果保存
            if "recommendations" in result:
                for rec in result.get('recommendations', []):
                    # シンボルを正規化
                    normalized_symbol = normalize_symbol(rec['symbol'])
                    result_stmt = insert(RecommendationResult).values(
                        session_id=session_id,
                        symbol=normalized_symbol,
                        name=rec.get('name', ''),
                        allocation=rec.get('allocation', ''),
                        confidence=rec.get('confidence') / 100.0 if rec.get('confidence') else None,
                        reason=rec.get('reason', "")
                    )
                    conn.execute(result_stmt)
            return True
            
    except Exception as e:
        logger.error(f"推奨結果の保存に失敗: {str(e)}")
        return False
