from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pandas as pd
from chart_plotter import plot_candlestick
import base64
from dotenv import load_dotenv
from utils import setup_backend_logger
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List  # Listを追加
from technical_indicators import calculate_moving_average
from stock_recommender import recommend_stocks  # recommend_stocksをインポート

# ロギング設定の初期化（バックエンド全体で共通）
logger = setup_backend_logger()

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

@app.get("/stocks", response_model=dict)
async def get_stocks(
    page: int = 1, 
    limit: int = 20, 
    search: Optional[str] = None,
    sort_by: Optional[str] = "symbol",
    sort_order: Optional[str] = "asc"
):
    """銘柄一覧を取得するエンドポイント（ページネーション・ソート対応）"""
    conn = None
    try:
        # リクエスト情報をログに出力
        logger.info(f"受信リクエスト: GET /stocks?page={page}&limit={limit}&search={search}&sort_by={sort_by}&sort_order={sort_order}")
        
        # 有効なソートカラムのリスト
        valid_columns = ["symbol", "name", "industry", "golden_cross", "dead_cross", "rsi", "macd", "signal_line"]
        
        # ソートカラムの検証
        if sort_by and sort_by not in valid_columns:
            raise HTTPException(
                status_code=400,
                detail=f"無効なソートカラム: {sort_by}"
            )
            
        # ソート順の検証
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=400,
                detail=f"無効なソート順: {sort_order}"
            )
            
        # ソート順の正規化
        sort_order = sort_order.upper()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 検索条件の構築
        search_condition = ""
        search_params = ()
        if search and search.strip():
            search_term = f"%{search.strip().lower()}%"
            search_condition = "WHERE LOWER(s.symbol) LIKE %s OR LOWER(s.name) LIKE %s"
            search_params = (search_term, search_term)
        
        # 総件数取得
        count_query = f"SELECT COUNT(*) FROM stocks s {search_condition}"
        if search and search.strip():
            cursor.execute(count_query, search_params)
        else:
            cursor.execute(count_query)
        total = cursor.fetchone()['count']
        
        # データ取得（オフセット計算）
        offset = (page - 1) * limit
        data_query = f"""
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
            {search_condition}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        logger.info(f"クエリを実行します: {data_query}")
        logger.info(f"検索パラメータ: {search_params}")
        
        # クエリ実行
        if search and search.strip():
            cursor.execute(data_query, search_params + (limit, offset))
        else:
            cursor.execute(data_query, (limit, offset))
        
        stocks = cursor.fetchall()
        # 銘柄データをログ出力
        df = pd.DataFrame(stocks)
        logger.info(f"銘柄データ:\n{df}")
        
        logger.info(f"{len(stocks)}件の銘柄データを取得しました (ページ {page}/{total//limit + 1})")
        return {
            "stocks": stocks,
            "total": total,
            "page": page,
            "limit": limit
        }
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

# 推奨リクエストモデル
class RecommendationRequest(BaseModel):
    principal: float
    risk_tolerance: str  # 例: "低", "中", "高"
    strategy: str  # 例: "成長株", "配当株", "バランス"
    symbols: Optional[List[str]] = None  # 特定銘柄指定（オプション）

@app.post("/api/recommend", response_model=dict)
async def get_recommendations(request: RecommendationRequest):
    """AIによる銘柄推奨を取得"""
    try:
        logger.info(f"受信リクエスト: POST /api/recommend - {request.dict()}")
        
        # 推奨生成
        result = await recommend_stocks(request.dict())
        
        if "error" in result.get("data", {}):
            raise HTTPException(
                status_code=500,
                detail=result["data"]["error"]
            )
            
        return result
    except Exception as e:
        logger.exception(f"推奨生成エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"推奨生成エラー: {str(e)}"
        )

@app.get("/chart/{symbol}", response_model=dict)
async def get_chart(symbol: str):
    """銘柄のチャート画像をBase64で取得"""
    try:
        logger.info(f"受信リクエスト: GET /chart/{symbol}")
        
        # 1. 銘柄情報取得（会社名取得用）
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM stocks WHERE symbol = %s", (symbol,))
        stock_info = cursor.fetchone()
        
        if not stock_info:
            raise HTTPException(status_code=404, detail="銘柄が見つかりません")
        
        company_name = stock_info['name']
        
        # 2. チャートデータ取得
        cursor.execute("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE symbol = %s
              AND date >= CURRENT_DATE - INTERVAL '3 years'  -- システム日付から3年前まで
            ORDER BY date ASC  -- 昇順でソート
        """, (symbol,))
        chart_data = cursor.fetchall()
        
        # 3. チャート生成
        df = pd.DataFrame(chart_data)
        logger.info(f"チャートデータ:\n{df}")

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        # 移動平均計算
        df['MA30'] = calculate_moving_average(df['close'])
        
        # チャート生成
        output_path = plot_candlestick(df, symbol, company_name)
        
        # 出力パスがNoneの場合のエラーハンドリング
        if output_path is None:
            error_msg = f"チャート生成に失敗しました: symbol={symbol}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
        # Base64エンコード
        with open(output_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "image": f"data:image/png;base64,{encoded_string}"
        }
    except Exception as e:
        logger.exception(f"チャート生成エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"チャート生成エラー: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
