import logging
from typing import Dict
from aiagent.factory import RecommenderFactory
from aiagent.data_access import save_recommendation

logger = logging.getLogger(__name__)

async def recommend_stocks(params: Dict) -> Dict:
    """銘柄推奨を生成 (ファクトリ経由で実装を選択)
    
    Args:
        params: 推奨パラメータ (agent_typeを含む可能性あり)
        
    Returns:
        推奨結果を含む辞書
    """
    logger.info("Starting stock recommendation process")
    agent_type = params.get('agent_type', 'direct')
    logger.info(f"Selected agent type: {agent_type}")
    recommender = RecommenderFactory.create(agent_type)
    logger.info(f"Created recommender: {recommender.__class__.__name__}")
    logger.info("Executing recommendation...")
    result = await recommender.execute(params)
    logger.info("Recommendation execution completed")
    
    # 推奨結果をDBに保存
    logger.info("Saving recommendation to database...")
    if result.get('status') != 'error':
        save_recommendation(result, params)
        logger.info("Recommendation saved successfully")
    else:
        logger.error("Recommendation failed with error status")
    
    logger.info("Recommendation process completed")
    return result
