from .interface import IStockRecommender
from .deepseek_direct import DeepSeekDirectRecommender
from .mcp_agent import McpAgent
import os

class RecommenderFactory:
    @staticmethod
    def create() -> IStockRecommender:
        """設定に基づいて推奨クラスのインスタンスを生成
        
        Returns:
            IStockRecommender: 推奨クラスのインスタンス
        """
        mode = os.getenv('AGENT_TYPE', 'direct').lower()
        
        if mode == 'direct':
            return DeepSeekDirectRecommender()
        elif mode == 'mcpagent':
            return McpAgent()
        
        raise ValueError(f"Unknown recommender mode: {mode}")
