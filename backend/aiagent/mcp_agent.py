from .interface import IStockRecommender
from typing import Dict, Any

class McpAgent(IStockRecommender):
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCPエージェントのダミー実装
        
        Args:
            params: 推奨パラメータ
            
        Returns:
            指定された形式のダミーデータ
        """
        return {
            "recommendations": [
                {
                    "symbol": "7203.T",
                    "name": "トヨタ自動車",
                    "confidence": 85,
                    "allocation": "30%",
                    "reason": "業績好調および株価上昇トレンド"
                },
                {
                    "symbol": "9984.T",
                    "name": "ソフトバンクグループ",
                    "confidence": 78,
                    "allocation": "25%",
                    "reason": "AI投資の拡大期待"
                },
                {
                    "symbol": "6861.T",
                    "name": "キーエンス",
                    "confidence": 92,
                    "allocation": "20%",
                    "reason": "高収益率と安定成長"
                }
            ],
            "total_return_estimate": "15.2%"
        }
