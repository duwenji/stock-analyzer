from mcp_agent.workflows.llm.augmented_llm import AugmentedLLM
import os
import httpx
import asyncio
from typing import Optional, Dict, Any

class DeepSeekAugmentedLLM(AugmentedLLM):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        
    async def generate(self, prompt: str, **kwargs) -> str:
        model = kwargs.get('model', 'deepseek-r1')
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 2000)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
    async def generate_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1 * (attempt + 1))
