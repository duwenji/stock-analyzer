from .interface import IStockRecommender
from .deepseek_direct import DeepSeekDirectRecommender
import os

class RecommenderFactory:
    @staticmethod
    def create() -> IStockRecommender:
        """設定に基づいて推奨クラスのインスタンスを生成
        
        Returns:
            IStockRecommender: 推奨クラスのインスタンス
        """
        mode = os.getenv('RECOMMENDER_MODE', 'direct').lower()
        
        if mode == 'direct':
            return DeepSeekDirectRecommender()
        # 将来のMCP実装用
        # elif mode == 'mcp':
        #     return MCPRecommender()
        
        raise ValueError(f"Unknown recommender mode: {mode}")
