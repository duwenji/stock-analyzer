from fastapi import FastAPI, HTTPException, Depends
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from models import PromptTemplate
from typing import List
import os
import pandas as pd
from chart_plotter import plot_candlestick
import base64
from utils import setup_backend_logger, get_db_engine, get_ma_settings
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from technical_indicators import calculate_moving_average, calculate_macd, calculate_rsi
from stock_recommender import recommend_stocks

# ロギング設定の初期化（バックエンド全体で共通）
logger = setup_backend_logger(__name__)

# レスポンスモデルの定義
class StockResponse(BaseModel):
    symbol: str
    name: str
    industry: str
    technical_date: Optional[str] = None
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

@app.get("/api/stocks", response_model=dict)
async def get_stocks(
    page: int = 1, 
    limit: int = 20, 
    search: Optional[str] = None,
    industry_code: Optional[str] = None,
    scale_code: Optional[str] = None,
    sort_by: Optional[str] = "symbol",
    sort_order: Optional[str] = "asc"
):
    """銘柄一覧を取得するエンドポイント（ページネーション・ソート対応）"""
    try:
        # リクエスト情報をログに出力
        logger.info(f"受信リクエスト: GET /stocks?page={page}&limit={limit}&search={search}&sort_by={sort_by}&sort_order={sort_order}")
        
        # 有効なソートカラムのリスト
        valid_columns = ["symbol", "name", "industry", "technical_date", "golden_cross", "dead_cross", "rsi", "macd", "signal_line"]
        
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
        
        engine = get_db_engine()
        with engine.connect() as conn:
            # 検索条件の構築
            search_condition = ""
            search_params = {}
            if search and search.strip():
                search_term = f"%{search.strip().lower()}%"
                search_condition = "WHERE LOWER(s.symbol) LIKE :search_term OR LOWER(s.name) LIKE :search_term"
                search_params = {"search_term": search_term}
            
            if industry_code and industry_code.strip():
                industry_code_term = industry_code.strip()
                if not search_condition:
                    search_condition = "WHERE s.industry_code_33 = :industry_code"
                else:
                    search_condition += " AND s.industry_code_33 = :industry_code"
                search_params["industry_code"] = industry_code_term

            if scale_code and scale_code.strip():
                scale_code_term = scale_code.strip()
                if not search_condition:
                    search_condition = "WHERE s.scale_code = :scale_code"
                else:
                    search_condition += " AND s.scale_code = :scale_code"
                search_params["scale_code"] = scale_code_term
            
            # 総件数取得
            count_query = f"SELECT COUNT(*) FROM stocks s {search_condition}"
            result = conn.execute(text(count_query), search_params)
            total = result.scalar()
            
            # データ取得（オフセット計算）
            offset = (page - 1) * limit
            data_query = f"""
                SELECT 
                    s.symbol, 
                    s.name, 
                    industry_name_33 as industry,
                    s.scale_name,
                    ti.golden_cross,
                    ti.dead_cross,
                    ti.rsi,
                    ti.macd,
                    ti.signal_line,
                    TO_CHAR(ti.date, 'YYYY-MM-DD') as technical_date
                FROM stocks s
                LEFT JOIN (
                    SELECT DISTINCT ON (symbol) *
                    FROM technical_indicators
                    ORDER BY symbol, date DESC
                ) ti ON s.symbol = ti.symbol
                {search_condition}
                ORDER BY {sort_by} {sort_order} NULLS LAST
                LIMIT :limit OFFSET :offset
            """
            logger.info(f"クエリを実行します: {data_query}")
            logger.info(f"検索パラメータ: {search_params}")
            
            # クエリ実行
            params = {**search_params, "limit": limit, "offset": offset}
            result = conn.execute(text(data_query), params)
            stocks = [dict(row._mapping) for row in result]
            
            # 銘柄データをログ出力
            df = pd.DataFrame(stocks)
            logger.info(f"{len(stocks)}件の銘柄データを取得しました (ページ {page}/{total//limit + 1})")
            
            return {
                "stocks": stocks,
                "total": total,
                "page": page,
                "limit": limit
            }
    except SQLAlchemyError as e:
        logger.exception(f"データベースエラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"データベースエラー: {str(e)}"
        )
    except EnvironmentError as e:
        logger.exception(f"環境設定エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"環境設定エラー: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"銘柄一覧取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"銘柄一覧取得エラー: {str(e)}"
        )

# 推奨リクエストモデル
class RecommendationRequest(BaseModel):
    principal: float
    risk_tolerance: str     # 例: "低", "中", "高"
    strategy: str           # 例: "成長株", "配当株", "バランス"
    symbols: Optional[List[str]] = None     # 特定銘柄指定（オプション）
    search: Optional[str] = None        # 検索条件（追加）
    technical_filters: Optional[dict] = None
    agent_type: str = "direct"  # デフォルト値
    prompt_id: Optional[int] = None  # プロンプトテンプレートID
    optimizer_prompt_id: Optional[int] = None  # 最適化プロンプトID
    evaluation_prompt_id: Optional[int] = None  # 評価プロンプトID

class SelectedRecommendationRequest(RecommendationRequest):
    selected_symbols: List[str]
    # agent_typeとprompt_idは親クラスから継承

class PromptTemplateRequest(BaseModel):
    """プロンプトテンプレートリクエストモデル"""
    name: str
    agent_type: str = "direct"
    system_role: str = ""
    user_template: str
    output_format: str

class PromptTemplateResponse(BaseModel):
    """プロンプトテンプレートレスポンスモデル"""
    id: int
    name: str
    agent_type: str
    system_role: str
    user_template: str
    output_format: str
    created_at: str
    updated_at: str

def get_db():
    """データベースセッションを取得"""
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.post("/api/prepare-recommendations", response_model=dict)
async def prepare_recommendations(request: RecommendationRequest):
    """推奨銘柄準備エンドポイント"""
    try:
        logger.info(f"フィルタリングリクエスト受信: {request.model_dump()}")

        engine = get_db_engine()
        with engine.connect() as conn:
            # 検索条件で銘柄をフィルタリング
            search_params = {}
            where_clauses = []
            if request.search:
                search_term = f"%{request.search.strip().lower()}%"
                where_clauses.append("LOWER(s.symbol) LIKE :search_term OR LOWER(s.name) LIKE :search_term")
                search_params = {"search_term": search_term}

            # テクニカル指標でフィルタリング
            if request.technical_filters:
                for indicator, value in request.technical_filters.items():
                    if indicator == "rsi":
                        # RSIフィルタのバリデーション
                        if not isinstance(value, (list, tuple)) or len(value) != 2:
                            continue  # 不正な形式の場合はスキップ
                        op, val = value
                        if not op or val in (None, ''):
                            continue  # 演算子または値が空の場合はスキップ
                        try:
                            float(val)  # 数値に変換可能かチェック
                            where_clauses.append(f"ti.rsi {op} {val}")
                        except (ValueError, TypeError):
                            continue
                    elif indicator == "golden_cross":
                        # golden_crossフィルタのバリデーション
                        if value is True:
                            where_clauses.append("ti.golden_cross = true")
                        elif isinstance(value, (list, tuple)) and len(value) == 2 and str(value[1]).lower() == 'true':
                            where_clauses.append("ti.golden_cross = true")
                        elif str(value).lower() == 'true':
                            where_clauses.append("ti.golden_cross = true")

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            query = f"""
                SELECT 
                    s.symbol,
                    s.name,
                    s.industry_name_33 as industry,
                    ti.rsi,
                    ti.golden_cross,
                    TO_CHAR(ti.date, 'YYYY-MM-DD') as indicator_date
                FROM stocks s
                LEFT JOIN (
                    SELECT DISTINCT ON (symbol) *
                    FROM technical_indicators
                    ORDER BY symbol, date DESC
                ) ti ON s.symbol = ti.symbol
                {where_sql}
            """

            logger.info(f"テクニカル指標取得SQL：{text(query)}")
            result = conn.execute(text(query), search_params)
            stocks = [dict(row._mapping) for row in result]
            logger.info(f"銘柄件数：{len(stocks)}")

            return {
                "candidate_stocks": stocks,
                "params": request.model_dump()
            }

    except Exception as e:
        logger.exception(f"フィルタリングエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"フィルタリングエラー: {str(e)}")

@app.post("/api/recommend", response_model=dict)
async def recommend(request: SelectedRecommendationRequest):
    """選択された銘柄のみで推奨生成"""
    try:
        logger.info(f"推奨リクエスト受信: {request.model_dump()}")

        params = request.model_dump()
        params['symbols'] = request.selected_symbols
        params['agent_type'] = request.agent_type
        result = await recommend_stocks(params)

        if "error" in result.get("data", {}):
            raise HTTPException(status_code=500, detail=result["data"]["error"])

        return result

    except Exception as e:
        logger.exception(f"推奨生成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推奨生成エラー: {str(e)}")

@app.get("/api/industry-codes", response_model=list)
async def get_industry_codes():
    """業種コードと業種名の一覧を取得"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            query = "SELECT DISTINCT industry_code_33 as code, industry_name_33 as name FROM stocks ORDER BY code"
            result = conn.execute(text(query))
            return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.exception(f"業種コード取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="業種コードの取得に失敗しました")

# プロンプトテンプレート管理API
@app.get("/api/prompts", response_model=List[PromptTemplateResponse])
async def get_all_prompts(db: Session = Depends(get_db)):
    """全プロンプトテンプレートを取得"""
    try:
        prompts = db.query(PromptTemplate).order_by(PromptTemplate.id).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "agent_type":p.agent_type, 
                "system_role": p.system_role,
                "user_template": p.user_template,
                "output_format": p.output_format,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in prompts
        ]
    except Exception as e:
        logger.exception(f"プロンプト取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="プロンプトの取得に失敗しました")

@app.get("/api/prompts/{id}", response_model=PromptTemplateResponse)
async def get_prompt(id: int, db: Session = Depends(get_db)):
    """特定のプロンプトテンプレートを取得"""
    try:
        prompt = db.query(PromptTemplate).filter_by(id=id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="プロンプトが見つかりません")
        return {
            "id": prompt.id,
            "name": prompt.name,
            "agent_type":prompt.agent_type, 
            "system_role": prompt.system_role,
            "user_template": prompt.user_template,
            "output_format": prompt.output_format,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat()
        }
    except Exception as e:
        logger.exception(f"プロンプト取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="プロンプトの取得に失敗しました")

@app.post("/api/prompts", response_model=PromptTemplateResponse)
async def create_prompt(request: PromptTemplateRequest, db: Session = Depends(get_db)):
    """新規プロンプトテンプレートを作成"""
    try:
        existing = db.query(PromptTemplate).filter_by(name=request.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="同名のプロンプトが既に存在します")
            
        prompt = PromptTemplate(
            name=request.name,
            agent_type=request.agent_type,
            system_role=request.system_role,
            user_template=request.user_template,
            output_format=request.output_format,
            updated_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        prompt = db.query(PromptTemplate).filter_by(name=request.name).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="プロンプトが見つかりません")
        
        return {
            "id": prompt.id,
            "name": prompt.name,
            "agent_type": prompt.agent_type,
            "system_role": prompt.system_role,
            "user_template": prompt.user_template,
            "output_format": prompt.output_format,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        logger.exception(f"プロンプト作成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="プロンプトの作成に失敗しました")

@app.put("/api/prompts/{id}", response_model=PromptTemplateResponse)
async def update_prompt(id: int, request: PromptTemplateRequest, db: Session = Depends(get_db)):
    """プロンプトテンプレートを更新"""
    try:
        # トランザクション開始
        db.begin()
        
        prompt = db.query(PromptTemplate).filter_by(id=id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="プロンプトが見つかりません")
            
        # 更新処理
        prompt.agent_type = request.agent_type
        prompt.user_template = request.user_template
        prompt.output_format = request.output_format
        prompt.system_role = request.system_role
        prompt.updated_at = datetime.datetime.now(datetime.timezone.utc)
        
        # 変更を検証
        db.flush()
        
        # コミット
        db.commit()
        
        # 最新データを取得
        db.refresh(prompt)
        
        return {
            "id": prompt.id,
            "name": prompt.name,
            "system_role": prompt.system_role,
            "agent_type":prompt.agent_type, 
            "user_template": prompt.user_template,
            "output_format": prompt.output_format,
            "created_at": prompt.created_at.isoformat(),
            "updated_at": prompt.updated_at.isoformat()
        }
        
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"データベースエラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"データベースエラー: {e.orig.args[0] if hasattr(e, 'orig') else str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.exception(f"予期せぬエラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラー: {str(e)}"
        )

@app.delete("/api/prompts/{id}")
async def delete_prompt(id: int, db: Session = Depends(get_db)):
    """プロンプトテンプレートを削除"""
    try:
        prompt = db.query(PromptTemplate).filter_by(id=id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="プロンプトが見つかりません")
            
        db.delete(prompt)
        db.commit()
        return {"message": "プロンプトを削除しました"}
    except Exception as e:
        db.rollback()
        logger.exception(f"プロンプト削除エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="プロンプトの削除に失敗しました")

@app.get("/api/scale-codes", response_model=list)
async def get_scale_codes():
    """規模コードと規模名の一覧を取得"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            query = "SELECT DISTINCT scale_code as code, scale_name as name FROM stocks ORDER BY code"
            result = conn.execute(text(query))
            return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.exception(f"規模コード取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="規模コードの取得に失敗しました")

@app.get("/api/chart/{symbol}", response_model=dict)
async def get_chart(symbol: str):
    """銘柄のチャート画像をBase64で取得"""
    try:
        logger.info(f"受信リクエスト: GET /chart/{symbol}")
        
        engine = get_db_engine()
        with engine.connect() as conn:
            # 1. 銘柄情報取得（会社名取得用）
            result = conn.execute(text("SELECT name FROM stocks WHERE symbol = :symbol"), {"symbol": symbol})
            stock_info = result.mappings().first()
            
            if not stock_info:
                raise HTTPException(status_code=404, detail="銘柄が見つかりません")
            
            company_name = stock_info['name']
            
            # 2. チャートデータ取得
            result = conn.execute(text("""
                SELECT date, open, high, low, close, volume
                FROM stock_prices
                WHERE symbol = :symbol
                  AND date >= CURRENT_DATE - INTERVAL '1 year'
                ORDER BY date ASC
            """), {"symbol": symbol})
            chart_data = [dict(row._mapping) for row in result]
        
            # 3. チャート生成
            df = pd.DataFrame(chart_data)
            logger.info(f"チャートデータ:\n{df}")

            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            # テクニカル指標計算
            ma_settings = get_ma_settings()
            df[f'MA{ma_settings["short"]}'] = calculate_moving_average(df['close'], window=ma_settings["short"])
            df[f'MA{ma_settings["long"]}'] = calculate_moving_average(df['close'], window=ma_settings["long"])
            df['macd'], df['signal_line'] = calculate_macd(df)  # MACD計算
            df['rsi'] = calculate_rsi(df)  # RSI計算
            
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
    except SQLAlchemyError as e:
        logger.exception(f"データベースエラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"データベースエラー: {str(e)}"
        )
    except EnvironmentError as e:
        logger.exception(f"環境設定エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"環境設定エラー: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"チャート生成エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"チャート生成エラー: {str(e)}"
        )

# 推奨履歴レスポンスモデル
class RecommendationHistoryResponse(BaseModel):
    session_id: str
    generated_at: str
    principal: float
    risk_tolerance: str
    strategy: str
    technical_filter: Optional[str] = None
    symbol_count: int

@app.get("/api/recommendations/history", response_model=dict)
async def get_recommendation_history(
    page: int = 1,
    limit: int = 10,
    sort: str = "date_desc",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    strategy: Optional[str] = None
):
    """推奨履歴一覧を取得"""
    try:
        # ソート条件の解析とバリデーション
        valid_sort_fields = ["generated_at", "principal", "risk_tolerance", "strategy"]
        valid_sort_orders = ["asc", "desc"]
        
        try:
            if "_" in sort:
                sort_field, sort_order = sort.split("-")
                if sort_order.lower() not in valid_sort_orders:
                    raise ValueError("無効なソート順序")
            else:
                sort_field = sort
                sort_order = "desc"
                
            if sort_field not in valid_sort_fields:
                raise ValueError("無効なソート項目")
                
            logger.info(f"ソート条件: field={sort_field}, order={sort_order}")
        except ValueError as e:
            logger.warning(f"無効なソートパラメータ: {sort} ({str(e)})")
            raise HTTPException(
                status_code=400,
                detail=f"無効なソートパラメータ: {sort}. 有効な形式: field_asc または field_desc (field: {', '.join(valid_sort_fields)})"
            )

        # クエリ構築
        where_clauses = []
        params = {}
        if start_date:
            where_clauses.append("generated_at >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("generated_at <= :end_date")
            params["end_date"] = end_date
        if strategy:
            where_clauses.append("strategy = :strategy")
            params["strategy"] = strategy

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        engine = get_db_engine()
        with engine.connect() as conn:
            # 総件数取得
            count_query = f"SELECT COUNT(*) FROM recommendation_sessions {where_sql}"
            total = conn.execute(text(count_query), params).scalar()

            # データ取得
            offset = (page - 1) * limit
            query = f"""
                SELECT 
                    session_id,
                    TO_CHAR(generated_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as generated_at,
                    principal,
                    risk_tolerance,
                    strategy,
                    technical_filter,
                    (SELECT COUNT(*) FROM recommendation_results rr 
                     WHERE rr.session_id = rs.session_id) as symbol_count
                FROM recommendation_sessions rs
                {where_sql}
                ORDER BY {sort_field} {sort_order}
                LIMIT :limit OFFSET :offset
            """
            params.update({"limit": limit, "offset": offset})
            result = conn.execute(text(query), params)
            sessions = [dict(row._mapping) for row in result]

            return {
                "total": total,
                "page": page,
                "limit": limit,
                "sessions": sessions
            }

    except Exception as e:
        logger.exception(f"推奨履歴取得エラー: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "推奨履歴の取得に失敗しました",
                "detail": str(e),
                "sessions": []  # 空配列を返す
            }
        )

@app.get("/api/recommendations/{session_id}", response_model=dict)
async def get_recommendation_detail(session_id: str):
    """特定セッションの推奨詳細を取得"""
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            # セッション基本情報取得
            session_query = """
                SELECT 
                    session_id,
                    TO_CHAR(generated_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as generated_at,
                    principal,
                    risk_tolerance,
                    strategy,
                    technical_filter
                FROM recommendation_sessions
                WHERE session_id = :session_id
            """
            session_result = conn.execute(text(session_query), {"session_id": session_id})
            session_info = session_result.mappings().first()
            
            if not session_info:
                raise HTTPException(status_code=404, detail="セッションが見つかりません")

            # 推奨結果取得
            results_query = """
                SELECT 
                    rr.symbol,
                    rr.name,
                    rr.allocation,
                    rr.confidence,
                    rr.reason
                FROM recommendation_results rr
                WHERE rr.session_id = :session_id
                ORDER BY rr.allocation DESC, rr.confidence DESC
            """
            results = conn.execute(text(results_query), {"session_id": session_id})
            recommendations = [dict(row._mapping) for row in results]

            return {
                "session": dict(session_info),
                "recommendations": recommendations
            }

    except Exception as e:
        logger.exception(f"推奨詳細取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"推奨詳細取得エラー: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from utils import initialize_environment

    # 環境初期化
    initialize_environment()
    uvicorn.run(app, host="0.0.0.0", port=8000)
