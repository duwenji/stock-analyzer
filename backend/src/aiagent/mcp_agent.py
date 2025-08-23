import json
import re
from aiagent.interface import IStockRecommender
from typing import Dict, Any
from aiagent.prompt_builder import build_recommendation_prompt
from utils import setup_backend_logger
from mcp_agent.workflows.evaluator_optimizer.evaluator_optimizer import (
    EvaluatorOptimizerLLM,
    QualityRating,
)

from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from aiagent.data_access import (fetch_company_infos, get_prompt_template)
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

logger = setup_backend_logger(__name__)

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
            "company_infos": fetch_company_infos(params['selected_symbols'])
        }
        
        # メッセージ構築
        msg4optimizer = build_recommendation_prompt(
            optimizer_prompt['system_role'],
            params=params,
            data=stock_data
        )
        msg4evaluation = build_recommendation_prompt(
            evaluation_prompt['system_role'],
            params=params,
            data=stock_data
        )
        message = build_recommendation_prompt(
            optimizer_prompt["user_template"],
            params=params,
            data=stock_data
        ) + "\n" + "【出力形式】\n" + optimizer_prompt['output_format']
        
        logger.info(f"optimizer’s instruction={msg4optimizer}")
        logger.info(f"evaluator's instruction={msg4evaluation}")
        logger.info(f"generator's message={message}")
        
        # 分析実行
        optimizer = Agent(
            name="stock_optimizer",
            instruction=msg4optimizer,
            server_names=["yfinance", "fetch"]
        )
        
        evaluator = Agent(
            name="risk_evaluator",
            instruction=msg4evaluation,
        )
        
        evaluator_optimizer = EvaluatorOptimizerLLM(
            optimizer=optimizer,
            evaluator=evaluator,
            llm_factory=OpenAIAugmentedLLM,
            min_rating=QualityRating.GOOD,
            max_refinements=10
        )
        
        result = await evaluator_optimizer.generate_str(
            message=message,
            request_params=RequestParams(model='gpt-4o'),
        )
        logger.info(f"MCPAgentRecommender's result={result}")
        
        try:
            # JSON部分を抽出してパース
            json_match = re.search(r'```json\s*({.*?})\s*```', result, re.DOTALL)
            if json_match:
                parsed_result = json.loads(json_match.group(1))
                # 生の評価結果を含めて返す
                return {
                    "parsed_result": parsed_result,
                    "raw_response": result
                }
            else:
                # JSON形式が見つからない場合のフォールバック
                return {
                    "parsed_result": {"status": "success", "data": result},
                    "raw_response": result
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {str(e)}")
            return {
                "parsed_result": {"status": "error", "message": "推奨結果の解析に失敗しました"},
                "raw_response": result
            }
