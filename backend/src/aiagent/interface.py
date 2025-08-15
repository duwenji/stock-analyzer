from abc import ABC, abstractmethod
from typing import Dict, Any

class IStockRecommender(ABC):
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """銘柄推奨を実行するインターフェース
        
        Args:
            params: 推奨パラメータ (元金、リスク許容度など)
            
        Returns:
            推奨結果を含む辞書
        """
