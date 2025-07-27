import asyncio
from mcp import Server
from news_fetcher import setup_tools

async def main():
    # MCPサーバー初期化
    server = Server("news_fetcher", port=8080)
    
    # ツールセットアップ
    setup_tools(server)
    
    # サーバー起動
    await server.start()
    print(f"News Fetcher MCP Server running on port 8080")
    
    # 永続実行
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
