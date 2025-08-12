from .interface import IStockRecommender
from .deepseek_direct import DeepSeekDirectRecommender
from .mcp_agent import MCPAgentRecommender
import os

class RecommenderFactory:
    @staticmethod
    def create(agent_type: str = 'direct') -> IStockRecommender:
        """設定に基づいて推奨クラスのインスタンスを生成
        
        Args:
            agent_type: 使用するエージェントタイプ ('direct' または 'mcpagent')
            
        Returns:
            IStockRecommender: 推奨クラスのインスタンス
        """
        mode = agent_type.lower()
        
        if mode == 'direct':
            return DeepSeekDirectRecommender()
        elif mode == 'mcpagent':
            return MCPAgentRecommender()
        
        raise ValueError(f"Unknown recommender mode: {mode}")
