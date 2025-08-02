from typing import Dict
from aiagent.factory import RecommenderFactory

async def recommend_stocks(params: Dict) -> Dict:
    """銘柄推奨を生成 (ファクトリ経由で実装を選択)
    
    Args:
        params: 推奨パラメータ
        
    Returns:
        推奨結果を含む辞書
    """
    recommender = RecommenderFactory.create()
    return await recommender.execute(params)
