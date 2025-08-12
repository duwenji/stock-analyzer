from typing import Dict
from sqlalchemy.orm import Session
from models import PromptTemplate
from utils import setup_backend_logger, get_db_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = setup_backend_logger(__name__)

def build_recommendation_prompt(params: Dict, data: Dict) -> str:
    """DBからプロンプトテンプレートを取得し、推奨プロンプトを構築
    
    Args:
        params: ユーザー入力パラメータ
        data: 銘柄データ
        
    Returns:
        構築されたプロンプト文字列
    """
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        template = db.query(PromptTemplate).filter_by(name="recommendation").first()
        if not template:
            raise ValueError("推奨プロンプトテンプレートがDBに見つかりません")
        
        prompt = (
            template.user_template.format(
                principal=params.get('principal', 'N/A'),
                risk_tolerance=params.get('risk_tolerance', '中'),
                strategy=params.get('strategy', '成長株重視'),
                company_infos=data.get('company_infos', []),
                technical_indicators=data.get('technical_indicators', [])
            ) + "\n\n" +
            "output_format:" + template.output_format
        )
        
        logger.debug(f"構築されたプロンプト: {prompt[:200]}...")  # ログには先頭200文字のみ表示
        return prompt
        
    except Exception as e:
        logger.error(f"プロンプト構築エラー: {str(e)}", exc_info=True)
        raise ValueError(f"プロンプト構築に失敗しました: {str(e)}")
    finally:
        db.close()
