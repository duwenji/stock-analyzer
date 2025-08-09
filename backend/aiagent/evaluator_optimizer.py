from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM,
    QualityRating
)
from mcp_agent.agents.agent import Agent
from .deepseek_augmented import DeepSeekAugmentedLLM
from enum import IntEnum
import asyncio

class StockQualityRating(IntEnum):
    LOW_RISK = 1
    HIGH_RETURN = 2
    BALANCED = 3
    
    @classmethod
    def from_scores(cls, risk_score: int, return_score: int):
        if risk_score <= 3 and return_score >= 8:
            return cls.BALANCED
        elif risk_score <= 2:
            return cls.LOW_RISK
        elif return_score >= 9:
            return cls.HIGH_RETURN
        return None

class StockEvaluatorOptimizer(EvaluatorOptimizerLLM):
    def __init__(self):
        optimizer = Agent(
            name="stock_optimizer",
            instruction="""株式データを分析し、リスクと収益のバランスが取れた投資推奨を生成してください。
            以下の要素を考慮:
            - テクニカル指標 (移動平均線, RSIなど)
            - ボラティリティ分析
            - 市場環境
            - 業績見通し""",
            server_names=["stock_analysis"]
        )
        
        evaluator = Agent(
            name="risk_evaluator",
            instruction="""投資推奨を以下の基準で評価:
            1. リスク評価 (1-10点):
               - ボラティリティ
               - ダウンサイドリスク
            2. 収益評価 (1-10点):
               - 短期収益率
               - 長期成長性
            3. 総合評価:
               - リスクスコアと収益スコアからStockQualityRatingを決定""",
        )
        
        super().__init__(
            optimizer=optimizer,
            evaluator=evaluator,
            llm_factory=DeepSeekAugmentedLLM,
            min_rating=StockQualityRating.BALANCED
        )

async def run_stock_analysis(stock_data: dict):
    analyzer = StockEvaluatorOptimizer()
    result = await analyzer.generate_str(
        message=f"以下の株価データを分析してください:\n{stock_data}",
        request_params={"model": "deepseek-r1"}
    )
    return result
