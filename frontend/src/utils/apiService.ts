import axios from 'axios';

// 既存のAPI関数...

// プロンプト管理API
export const promptService = {
  getAllPrompts: async () => {
    const response = await axios.get('/api/prompts');
    return response.data;
  },
  
  getPrompt: async (id: number) => {
    const response = await axios.get(`/api/prompts/${id}`);
    return response.data;
  },
  
  updatePrompt: async (id: number, data: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => {
    const response = await axios.put(`/api/prompts/${id}`, data);
    return response.data;
  },
  
  deletePrompt: async (id: number) => {
    const response = await axios.delete(`/api/prompts/${id}`);
    return response.data;
  },
  
  createPrompt: async (data: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => {
    const response = await axios.post('/api/prompts', data);
    return response.data;
  }
};
