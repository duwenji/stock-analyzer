import os
import asyncio
import json
import httpx
from typing import Dict, List
from utils import db_connector

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

class StockRecommender:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.db = db_connector()
    
    async def generate_recommendations(self, params: Dict) -> Dict:
        """銘柄推奨を生成"""
        # データ取得
        data = await self._fetch_data(params.get("symbols", []))
        
        # DeepSeek API呼び出し
        recommendations = await self._call_deepseek(params, data)
        
        return {
            "status": "success",
            "data": recommendations
        }
    
    async def _fetch_data(self, symbols: List[str]) -> Dict:
        """マルチソースからデータ取得"""
        # ニュース取得 (MCP Agent経由)
        news = await self._fetch_news()
        
        # テクニカル指標取得
        tech_indicators = self._fetch_technical_indicators(symbols)
        
        # 株価履歴取得
        price_history = self._fetch_price_history(symbols)
        
        return {
            "news": news,
            "technical_indicators": tech_indicators,
            "price_history": price_history
        }
    
    async def _fetch_news(self) -> List[Dict]:
        """MCP Agentからニュース取得"""
        # 実際の実装ではMCPツールを呼び出す
        return [
            {
                "title": "市場好調のニュース",
                "summary": "株式市場が好調...",
                "source": "Bloomberg"
            }
        ]
    
    def _fetch_technical_indicators(self, symbols: List[str]) -> List[Dict]:
        """DBからテクニカル指標取得"""
        if not symbols:
            return []
            
        query = f"""
            SELECT * FROM technical_indicators
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
            ORDER BY date DESC
            LIMIT 30
        """
        return self.db.query(query)
    
    def _fetch_price_history(self, symbols: List[str]) -> List[Dict]:
        """DBから株価履歴取得"""
        if not symbols:
            return []
            
        query = f"""
            SELECT * FROM stock_prices
            WHERE symbol IN ({','.join([f"'{s}'" for s in symbols])})
            ORDER BY date DESC
            LIMIT 90
        """
        return self.db.query(query)
    
    async def _call_deepseek(self, params: Dict, data: Dict) -> Dict:
        """DeepSeek APIを呼び出し"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = self._build_prompt(params, data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                return {"error": "API呼び出し失敗"}
            
            result = response.json()
            return self._parse_response(result)
    
    def _build_prompt(self, params: Dict, data: Dict) -> str:
        """プロンプトを構築"""
        return f"""
あなたはプロの株式アナリストです。以下の要素に基づき投資銘柄を推奨してください：

### ユーザー情報:
- 元金: {params.get('principal', 'N/A')}円
- リスク許容度: {params.get('risk_tolerance', '中')}
- 投資方針: {params.get('strategy', '成長株重視')}

### 利用可能データ:
1. ニュース: {json.dumps(data.get('news', []), ensure_ascii=False, indent=2)}
2. テクニカル指標: {json.dumps(data.get('technical_indicators', []), ensure_ascii=False, indent=2)}
3. 過去価格: {json.dumps(data.get('price_history', []), ensure_ascii=False, indent=2)}

### 出力形式:
{{
  "recommendations": [
    {{
      "symbol": "銘柄コード",
      "name": "会社名",
      "confidence": 0-100,
      "allocation": "推奨割合%",
      "reason": "推奨理由"
    }}
  ],
  "total_return_estimate": "期待リターン%"
}}
"""
    
    def _parse_response(self, api_response: Dict) -> Dict:
        """APIレスポンスを解析"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return {"error": "レスポンス解析エラー"}

# 非同期実行ヘルパー
async def recommend_stocks(params: Dict) -> Dict:
    recommender = StockRecommender()
    return await recommender.generate_recommendations(params)
