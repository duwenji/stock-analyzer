import type { RecommendationParams } from '../RecommendationForm';

type TechnicalFilter = {
  [key: string]: [string, number | boolean];
};

export interface TransformedRequest {
  principal: number;
  risk_tolerance: string;
  strategy: string;
  agent_type: string;
  symbols?: string[];
  search?: string;
  technical_filters?: TechnicalFilter;
  prompt_id?: number;  // プロンプトIDを追加
}

export const transformRecommendationRequest = (
  data: RecommendationParams
): TransformedRequest => {
  // 数値変換のバリデーション
  const principal = parseFloat(data.principal);
  if (isNaN(principal)) {
    throw new Error('投資元金には有効な数値を入力してください');
  }
  if (principal <= 0) {
    throw new Error('投資元金は0より大きい値を入力してください');
  }

  return {
    principal,
    risk_tolerance: data.riskTolerance,
    strategy: data.strategy,
    agent_type: data.agentType || "direct",
    symbols: data.symbols 
      ? data.symbols.split(',').map((s: string) => s.trim()).filter((s: string) => s.length > 0)
      : undefined,
    search: data.search,
    technical_filters: data.technical_filters,
    prompt_id: data.promptId  // プロンプトIDを追加
  };
};
