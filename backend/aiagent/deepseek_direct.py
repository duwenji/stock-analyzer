import os
import json
import httpx
import pandas as pd
from typing import Dict, List
from openai import OpenAI
from .interface import IStockRecommender
from utils import get_db_engine, setup_backend_logger

logger = setup_backend_logger()

DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-reasoner"

class DeepSeekDirectRecommender(IStockRecommender):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.engine = get_db_engine()
        self.ai_client = OpenAI(api_key=self.api_key, base_url=DEEPSEEK_API_URL)
    
    async def execute(self, params: Dict) -> Dict:
        """直接DeepSeek APIを呼び出して銘柄推奨を生成"""
        try:
            logger.info(f"Generating recommendations with params: {params}")
            
            # テクニカル指標によるフィルタリング
            symbols = await self._filter_symbols(params)
            
            # データ取得
            data = await self._fetch_data(symbols)
            
            # API呼び出し
            return await self._call_deepseek(params, data)
            
        except Exception as e:
            logger.exception(f"Recommendation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _filter_symbols(self, params: Dict) -> List[str]:
        """テクニカル指標で銘柄をフィルタリング"""
        logger.debug(f"Filtering symbols with params: {params}")
        filters = params.get("technical_filters", {})
        
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
        """必要なデータを取得"""
        return {
            "news": await self._fetch_news(),
            "technical_indicators": self._fetch_technical_indicators(symbols),
            "price_history": self._fetch_price_history(symbols)
        }

    async def _fetch_news(self) -> List[Dict]:
        """ニュースを取得"""
        return [{
            "title": "市場好調のニュース", 
            "summary": "株式市場が好調...",
            "source": "Bloomberg"
        }]

    def _fetch_technical_indicators(self, symbols: List[str]) -> List[Dict]:
        """テクニカル指標を取得"""
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
        """株価履歴を取得"""
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
        """DeepSeek APIを呼び出し"""
        prompt = self._build_prompt(params, data)
        logger.info(f"Prompt: {prompt}")

        response = self.ai_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "あなたはプロの株式アナリストです。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

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

    def _parse_response(self, response) -> Dict:
        """APIレスポンスを解析"""
        try:
            content = response.choices[0].message.content
            
            # Check for empty/invalid response
            if not content or not content.strip():
                logger.error("Empty response received from API")
                return {"error": "Empty API response"}
                
            # Extract JSON from Markdown code block if present
            if '```json' in content:
                json_start = content.find('{', content.find('```json'))
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
            else:
                # Try to find the first { and last } as fallback
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end] if json_start != -1 and json_end != 0 else content
                
            # Remove any comments or non-JSON content
            json_str = '\n'.join(line for line in json_str.split('\n') 
                         if not line.strip().startswith('//') and line.strip())
                
            # Validate JSON structure
            if not (json_str.startswith('{') and json_str.endswith('}')):
                logger.error(f"Invalid JSON structure in response: {json_str[:200]}...")
                return {"error": "Invalid JSON structure"}
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            logger.error(f"Response Content (truncated): {content[:200]}...")
            return {"error": f"JSON parse error: {str(e)}"}
        except Exception as e:
            logger.exception(f"Unexpected error parsing response: {str(e)}")
            return {"error": str(e)}
