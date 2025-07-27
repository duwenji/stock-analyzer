import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List, Dict
import json

class NewsFetcher:
    def __init__(self):
        self.sources = {
            "general": [
                "https://www.bloomberg.com/markets",
                "https://www.reuters.com/finance"
            ],
            "company": "https://finance.yahoo.com/quote/"
        }
        self.cache = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def fetch_general_news(self, keywords: str, max_results: int = 5, time_range: str = "1d") -> List[Dict]:
        """一般金融ニュースを取得"""
        cache_key = f"general_{keywords}_{max_results}_{time_range}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        tasks = []
        async with ClientSession() as session:
            for url in self.sources["general"]:
                tasks.append(self._fetch_source(session, url, keywords))
            
            results = await asyncio.gather(*tasks)
            news_items = [item for sublist in results for item in sublist][:max_results]
            
            # 簡易要約生成（後でNLP統合）
            for item in news_items:
                item["summary"] = item["content"][:150] + "..." if len(item["content"]) > 150 else item["content"]
            
            self.cache[cache_key] = news_items
            return news_items

    async def fetch_company_news(self, symbol: str, max_results: int = 3) -> List[Dict]:
        """企業固有ニュースを取得"""
        cache_key = f"company_{symbol}_{max_results}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.sources['company']}{symbol}"
        async with ClientSession() as session:
            news_items = await self._fetch_company_news(session, url, max_results)
            self.cache[cache_key] = news_items
            return news_items

    async def _fetch_source(self, session: ClientSession, url: str, keywords: str) -> List[Dict]:
        """個別ソースからニュースを取得"""
        try:
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # ダミーデータ（実際のパーシングロジックを後で実装）
                return [{
                    "title": f"サンプルニュース {i}",
                    "url": f"{url}/news/{i}",
                    "source": url.split('//')[1].split('/')[0],
                    "content": f"{keywords}に関するニュースコンテンツ...",
                    "timestamp": "2023-01-01T12:00:00Z"
                } for i in range(3)]
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return []

    async def _fetch_company_news(self, session: ClientSession, url: str, max_results: int) -> List[Dict]:
        """企業固有ニュースを取得"""
        # 実際の実装ではYahoo Financeパーシング
        return [{
            "title": f"{url.split('/')[-1]} に関するニュース",
            "url": f"{url}/news",
            "source": "Yahoo Finance",
            "content": "企業固有のニュースコンテンツ...",
            "timestamp": "2023-01-01T12:00:00Z"
        }]

# MCPツール登録用インターフェース
def setup_tools(server):
    fetcher = NewsFetcher()
    
    @server.tool()
    async def fetch_general_news(keywords: str, max_results: int = 5, time_range: str = "1d"):
        return await fetcher.fetch_general_news(keywords, max_results, time_range)
    
    @server.tool()
    async def fetch_company_news(symbol: str, max_results: int = 3):
        return await fetcher.fetch_company_news(symbol, max_results)
