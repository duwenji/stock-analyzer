import logging
from typing import Dict
from aiagent.factory import RecommenderFactory
from aiagent.data_access import save_recommendation, get_prompt_template

logger = logging.getLogger(__name__)

async def recommend_stocks(params: Dict) -> Dict:
    """銘柄推奨を生成 (ファクトリ経由で実装を選択)
    
    Args:
        params: 推奨パラメータ (agent_typeとprompt_idを含む可能性あり)
        
    Returns:
        推奨結果を含む辞書
    """
    agent_type = params.get('agent_type', 'direct')
    
    recommender = RecommenderFactory.create(agent_type)
    logger.info(f"Created recommender: {recommender.__class__.__name__}")

    result = await recommender.execute(params)
    
    # 推奨結果をDBに保存
    logger.info("Saving recommendation to database...")
    if result.get('status') != 'error':
        save_recommendation(result, params)
    else:
        logger.error("Recommendation failed with error status")
    
    logger.info("Recommendation process completed")
    return result
