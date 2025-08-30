import logging
from typing import Dict
from .aiagent.factory import RecommenderFactory
from .aiagent.data_access import save_recommendation, get_prompt_template

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
    
    # 新しいレスポンス形式に対応（生データを含む場合）
    parsed_result = result
    raw_response = None
    
    if "parsed_result" in result and "raw_response" in result:
        # 新しい形式: parsed_resultとraw_responseを含む
        parsed_result = result["parsed_result"]
        raw_response = result["raw_response"]
        logger.info("新しいレスポンス形式を検出: 生データを含みます")
    
    # 推奨結果をDBに保存
    logger.info("Saving recommendation to database...")
    if parsed_result.get('status') != 'error':
        save_recommendation(parsed_result, params, raw_response)
    else:
        save_recommendation({}, params, raw_response)
        logger.error(f"Recommendation failed with error status: {parsed_result.get('message', '不明なエラー')}")
    
    logger.info("Recommendation process completed")
    return parsed_result
