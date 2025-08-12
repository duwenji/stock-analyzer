import json
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import PromptTemplate, Base
from utils import setup_backend_logger, get_db_engine

logger = setup_backend_logger(__name__)

def migrate_prompt_to_db():
    """JSONプロンプトをDBに移行"""
    try:
        # 1. JSONファイルを読み込む
        prompt_path = os.path.abspath('prompts/recommendation_prompt.json')
        with open(prompt_path, encoding='utf-8') as f:
            template = json.load(f)
        
        # 2. DB接続を確立
        engine = get_db_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 3. 既存のプロンプトをチェック
        existing = db.query(PromptTemplate).filter_by(name="recommendation").first()
        if existing:
            logger.info("プロンプトは既にDBに存在します。移行はスキップされます。")
            return
        
        # 4. 新しいプロンプトを作成
        prompt = PromptTemplate(
            name="recommendation",
            user_template=template['user_template'],
            output_format=template['output_format']
        )
        
        db.add(prompt)
        db.commit()
        logger.info("プロンプトをDBに正常に移行しました")
        
    except Exception as e:
        logger.error(f"プロンプト移行エラー: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_prompt_to_db()
