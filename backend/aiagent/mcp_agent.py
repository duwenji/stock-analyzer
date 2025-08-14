from .interface import IStockRecommender
from typing import Dict, Any
from enum import IntEnum
from aiagent.prompt_builder import build_recommendation_prompt
from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM
)
from mcp_agent.agents.agent import Agent
from aiagent.data_access import (fetch_company_infos, fetch_technical_indicators, get_prompt_template)
from aiagent.deepseek_augmented import DeepSeekAugmentedLLM

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
    def __init__(self, optimizer_instruction: str, evaluator_instruction: str):
        optimizer = Agent(
            name="stock_optimizer",
            instruction=optimizer_instruction,
            server_names=["stock_analysis"]
        )
        
        evaluator = Agent(
            name="risk_evaluator",
            instruction=evaluator_instruction,
        )
        
        super().__init__(
            optimizer=optimizer,
            evaluator=evaluator,
            llm_factory=DeepSeekAugmentedLLM,
            min_rating=StockQualityRating.BALANCED
        )

class MCPAgentRecommender(IStockRecommender):
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCPエージェントの実装
        
        Args:
            params: 推奨パラメータ
                - optimizer_prompt_id: 最適化プロンプトID
                - evaluation_prompt_id: 評価プロンプトID
                - selected_stocks: 銘柄コードリスト
                - principal: プリンシパル
                - risk_tolerance: リスク許容度
                - strategy: 戦略
            
        Returns:
            推奨結果
        """
        # プロンプト取得
        optimizer_prompt = get_prompt_template(params['optimizer_prompt_id'])
        evaluation_prompt = get_prompt_template(params['evaluation_prompt_id'])
        
        stock_data = {
            "company_infos": fetch_company_infos(params['selected_symbols']),
            "technical_indicators": fetch_technical_indicators(params['selected_symbols'])
        }

        # メッセージ構築
        message = build_recommendation_prompt(
            optimizer_prompt,
            params=params,
            data=stock_data
        )
        
        # 分析実行
        analyzer = StockEvaluatorOptimizer(
            optimizer_instruction=optimizer_prompt['system_role'],
            evaluator_instruction=evaluation_prompt['system_role']
        )
        
        return await analyzer.generate_str(
            message=message,
            request_params={"model": "deepseek-r1"}
        )
