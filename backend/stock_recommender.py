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
    logger.info(f"Starting stock recommendation process. {params}")
    agent_type = params.get('agent_type', 'direct')
    prompt_id = params.get('prompt_id')
    
    if not prompt_id:
        logger.error("prompt_id is required")
        return {'status': 'error', 'message': 'prompt_id is required'}
    
    logger.info(f"Selected agent type: {agent_type}")
    logger.info(f"Using prompt ID: {prompt_id}")
    
    # プロンプトテンプレートを取得
    prompt_template = None
    if prompt_id:
        prompt_template = get_prompt_template(prompt_id)
        if prompt_template:
            params['prompt_template'] = prompt_template
            logger.info(f"Loaded prompt template: {prompt_template}")
        else:
            logger.error(f"Prompt template not found for ID: {prompt_id}")
            return {'status': 'error', 'message': f'Prompt template not found for ID: {prompt_id}'}
    
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
