from typing import Dict
from aiagent.factory import RecommenderFactory
from aiagent.data_access import save_recommendation

async def recommend_stocks(params: Dict) -> Dict:
    """銘柄推奨を生成 (ファクトリ経由で実装を選択)
    
    Args:
        params: 推奨パラメータ
        
    Returns:
        推奨結果を含む辞書
    """
    recommender = RecommenderFactory.create()
    result = await recommender.execute(params)
    
    # 推奨結果をDBに保存
    if result.get('status') != 'error':
        save_recommendation(result, params)
    
    return result
