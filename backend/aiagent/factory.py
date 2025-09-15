from aiagent.interface import IStockRecommender
from aiagent.deepseek_direct import DeepSeekDirectRecommender
from aiagent.mcp_agent import MCPAgentRecommender

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
