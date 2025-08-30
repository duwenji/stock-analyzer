import axios from 'axios';
import { Industry, Scale } from '../types';

// 環境変数からAPIベースURLを取得（Docker環境ではREACT_APP_API_URL、開発環境では空文字でproxyを使用）
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// 推奨関連API
export const recommendationService = {
  prepareRecommendations: async (data: any) => {
    const response = await axios.post(`${API_BASE_URL}/api/prepare-recommendations`, data);
    return response.data;
  },
  getHistory: async (params: any) => {
    const response = await axios.get(`${API_BASE_URL}/api/recommendations/history`, { params });
    return response.data;
  },
  createRecommendation: async (data: any) => {
    const response = await axios.post(`${API_BASE_URL}/api/recommend`, data);
    return response.data;
  }
};

// 銘柄関連API
export const stockService = {
  getStocks: async (params: any) => {
    const response = await axios.get(`${API_BASE_URL}/api/stocks`, { params });
    return response.data;
  },
  getIndustryCodes: async (): Promise<Industry[]> => {
    const response = await axios.get(`${API_BASE_URL}/api/industry-codes`);
    return response.data;
  },
  getScaleCodes: async (): Promise<Scale[]> => {
    const response = await axios.get(`${API_BASE_URL}/api/scale-codes`);
    return response.data;
  }
};

// チャート関連API
export const chartService = {
  getChart: async (symbol: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/chart/${symbol}`);
    return response.data;
  }
};

// プロンプト管理API
export const promptService = {
  getAllPrompts: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/prompts`);
    return response.data;
  },
  
  getPrompt: async (id: number) => {
    const response = await axios.get(`${API_BASE_URL}/api/prompts/${id}`);
    return response.data;
  },
  
  updatePrompt: async (id: number, data: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => {
    const response = await axios.put(`${API_BASE_URL}/api/prompts/${id}`, data);
    return response.data;
  },
  
  deletePrompt: async (id: number) => {
    const response = await axios.delete(`${API_BASE_URL}/api/prompts/${id}`);
    return response.data;
  },
  
  createPrompt: async (data: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => {
    const response = await axios.post(`${API_BASE_URL}/api/prompts`, data);
    return response.data;
  }
};
