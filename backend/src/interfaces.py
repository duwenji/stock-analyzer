from typing import List, Optional, Dict, Any
from pydantic import BaseModel

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

class GetStocksParams(BaseModel):
    """get_stocks エンドポイントのパラメータ型"""
    page: int = 1
    limit: int = 20
    search: Optional[str] = None
    industry_code: Optional[str] = None
    scale_code: Optional[str] = None
    sort_by: Optional[str] = "symbol"
    sort_order: Optional[str] = "asc"

class GetStocksResponse(BaseModel):
    """get_stocks エンドポイントのレスポンス型"""
    stocks: List[Dict[str, Any]]
    total: int
    page: int
    limit: int
