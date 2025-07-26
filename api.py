from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

# レスポンスモデルの定義
class StockResponse(BaseModel):
    symbol: str
    name: str
    industry: str
    golden_cross: Optional[bool] = None
    dead_cross: Optional[bool] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    signal_line: Optional[float] = None

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="Stock Analyzer API",
    description="株式分析システムのバックエンドAPI",
    version="1.0.0"
)

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORSミドルウェアが設定されました: すべてのオリジンを許可")

# データベース接続設定
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "stock_data"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def get_db_connection():
    """データベース接続を確立"""
    try:
        # 接続情報をログに出力 (パスワードはマスク)
        masked_config = DB_CONFIG.copy()
        masked_config["password"] = "******"
        logger.info(f"データベース接続を試行します: {masked_config}")
        
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        
        logger.info(f"データベース接続成功: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"データベース接続エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"データベース接続エラー: {str(e)}"
        )

@app.get("/stocks", response_model=List[StockResponse])
async def get_stocks():
    """銘柄一覧を取得するエンドポイント"""
    conn = None
    try:
        # リクエスト情報をログに出力
        logger.info("受信リクエスト: GET /stocks")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                s.symbol, 
                s.name, 
                s.industry,
                ti.golden_cross,
                ti.dead_cross,
                ti.rsi,
                ti.macd,
                ti.signal_line
            FROM stocks s
            LEFT JOIN (
                SELECT DISTINCT ON (symbol) *
                FROM technical_indicators
                ORDER BY symbol, date DESC
            ) ti ON s.symbol = ti.symbol
            ORDER BY s.symbol
            LIMIT 50
        """
        logger.info(f"クエリを実行します: {query}")
        
        # CORSヘッダーが設定されていることをログ出力
        logger.info("CORSヘッダーを設定: Access-Control-Allow-Origin: *")
        
        cursor.execute(query)
        stocks = cursor.fetchall()
        
        logger.info(f"{len(stocks)}件の銘柄データを取得しました")
        return stocks
    except HTTPException:
        raise  # 既に処理済みのHTTPExceptionは再スロー
    except Exception as e:
        logger.exception(f"銘柄一覧取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"銘柄一覧取得エラー: {str(e)}"
        )
    finally:
        if conn:
            conn.close()
            logger.info("データベース接続をクローズしました")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
