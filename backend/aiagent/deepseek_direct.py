import os
import json
from typing import Dict, List
from openai import OpenAI
from .interface import IStockRecommender
from utils import setup_backend_logger
from aiagent.data_access import (
    fetch_company_infos,
    fetch_news,
    fetch_technical_indicators
)
from aiagent.prompt_builder import build_recommendation_prompt

logger = setup_backend_logger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-reasoner"

class DeepSeekDirectRecommender(IStockRecommender):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.ai_client = OpenAI(api_key=self.api_key, base_url=DEEPSEEK_API_URL)
    
    async def execute(self, params: Dict) -> Dict:
        """直接DeepSeek APIを呼び出して銘柄推奨を生成"""
        try:
            logger.info(f"Generating recommendations with params: {params}")
            
            # ユーザー選択銘柄を直接取得
            symbols = params.get("selected_symbols", [])
            if not symbols:
                logger.error("選択された銘柄がありません")
                return {"status": "error", "message": "選択された銘柄がありません"}
            
            # データ取得
            data = await self._fetch_data(symbols)
            logger.info(f"銘柄データ: {data}")
            
            # API呼び出し
            return await self._call_deepseek(params, data)
            
        except Exception as e:
            logger.exception(f"Recommendation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _fetch_data(self, symbols: List[str]) -> Dict:
        """必要なデータを取得"""
        return {
            "company_infos": fetch_company_infos(symbols),
            "technical_indicators": fetch_technical_indicators(symbols, limit=50)
        }

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
        template = params.get('prompt_template')
        return build_recommendation_prompt(template, params, data)

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
