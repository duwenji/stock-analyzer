export interface Industry {
  code: string;
  name: string;
}

export interface Scale {
  code: string;
  name: string;
}

export interface Recommendation {
  symbol: string;
  name: string;
  confidence: number;
  allocation: string;
  reason: string;
}

export interface ApiResponse {
  recommendations: Recommendation[];
  total_return_estimate: string;
  ai_raw_response?: string;
}
