import os
import json
import httpx
import pandas as pd
from typing import Dict, List
from openai import OpenAI

from utils import get_db_engine, setup_backend_logger

logger = setup_backend_logger()

DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-reasoner"

class StockRecommender:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.engine = get_db_engine()

        logger.info(f"Calling DeepSeek API with masked API key: {self.api_key[:2]}***")
        self.ai_client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=DEEPSEEK_API_URL)
    
    async def generate_recommendations(self, params: Dict) -> Dict:
        """銘柄推奨を生成"""
        logger.info(f"Starting generate_recommendations with params: {params}")
        
        # テクニカル指標による銘柄フィルタリング
        symbols = await self._filter_symbols_by_technical_indicators(
            params.get("technical_filters", {})
        )
        
        # ユーザー指定銘柄がある場合は上書き
        user_symbols = params.get("symbols", [])
        if user_symbols:
            symbols = user_symbols
        
        # データ取得
        data = await self._fetch_data(symbols)
        
        # DeepSeek API呼び出し
        recommendations = await self._call_deepseek(params, data)
        logger.info(f"Completed generate_recommendations: {recommendations}")

        return {
            "status": "success",
            "data": recommendations
        }
        
    async def _filter_symbols_by_technical_indicators(self, filters: Dict) -> List[str]:
        """テクニカル指標に基づき銘柄をフィルタリング"""
        logger.debug(f"Filtering symbols with technical filters: {filters}")
        if not filters:
            logger.debug("No filters provided, returning empty list")
            return []
            
        # 最新のテクニカル指標を取得
        query = """
            SELECT DISTINCT ON (symbol) symbol, *
            FROM technical_indicators
            ORDER BY symbol, date DESC
        """
        tech_data = pd.read_sql_query(query, self.engine)
        
        # フィルタリング条件を適用
        filtered_symbols = []
        for _, row in tech_data.iterrows():
            meets_conditions = True
            for indicator, (operator, value) in filters.items():
                if operator == "<" and not (row[indicator] < value):
                    meets_conditions = False
                elif operator == ">" and not (row[indicator] > value):
                    meets_conditions = False
                elif operator == "==" and not (row[indicator] == value):
                    meets_conditions = False
                    
            if meets_conditions:
                filtered_symbols.append(row["symbol"])
                
        logger.info(f"Filtered {len(filtered_symbols)} symbols matching criteria")
        return filtered_symbols
    
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
        return pd.read_sql_query(query, self.engine).to_dict('records')
    
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
        return pd.read_sql_query(query, self.engine).to_dict('records')
    
    async def _call_deepseek(self, params: Dict, data: Dict) -> Dict:
        prompt = self._build_prompt(params, data)
        logger.info(f"prompt: {prompt}")

        response = self.ai_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "あなたはプロの株式アナリストです。ユーザが提供された要素に基づき投資銘柄を推奨してください。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        # logger.info(f"response: {response}")
        return self._parse_response(response)
    
    def _build_prompt(self, params: Dict, data: Dict) -> str:
        """プロンプトを構築"""
        return f"""
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
            content = api_response.choices[0].message.content
            logger.info(f"推奨コンテンツ: {content}")
            
            return json.loads(content)
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse API response: {str(e)}. Response: {api_response}")
            return {"error": "レスポンス解析エラー"}

# 非同期実行ヘルパー
async def recommend_stocks(params: Dict) -> Dict:
    recommender = StockRecommender()
    return await recommender.generate_recommendations(params)
