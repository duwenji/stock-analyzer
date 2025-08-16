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
    
    # 型チェックを追加
    if not isinstance(result, dict):
        logger.error(f"無効な結果型: {type(result)}")
        return {"status": "error", "message": "無効な推奨結果形式"}
    
    # 推奨結果をDBに保存
    logger.info("Saving recommendation to database...")
    if result.get('status') != 'error':
        save_recommendation(result, params)
    else:
        logger.error(f"Recommendation failed with error status: {result.get('message', '不明なエラー')}")
    
    logger.info("Recommendation process completed")
    return result
