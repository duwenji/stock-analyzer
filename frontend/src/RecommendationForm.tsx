import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../src/styles/components/RecommendationForm.css';
import { promptService, recommendationService } from './utils/apiService';
import RecommendationConfirmationDialog from './components/RecommendationConfirmationDialog';
import { transformRecommendationRequest, TransformedRequest } from './utils/requestTransform';

export interface Stock {
  symbol: string;
  name: string;
  industry: string;
  rsi?: number;
  golden_cross?: boolean;
}

interface Prompt {
  id: number;
  name: string;
  agent_type: string;
  system_role: string;
  user_template: string;
  output_format: string;
  created_at: string;
  updated_at: string;
}

interface Industry {
  code: string;
  name: string;
}

interface Scale {
  code: string;
  name: string;
}

export interface RecommendationParams {
  principal: string;
  riskTolerance: string;
  strategy: string;
  agentType: string;
  symbols: string;
  search: string;
  industries?: string[];
  scales?: string[];
  promptId?: number;
  optimizerPromptId?: number;
  evaluationPromptId?: number;
  technical_filters?: {
    [key: string]: [string, any];
  };
}

const RecommendationForm: React.FC<{ 
  onSubmit: (params: TransformedRequest & { selected_symbols: string[] }) => void 
}> = ({ onSubmit }) => {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [scales, setScales] = useState<Scale[]>([]);
  const [formData, setFormData] = useState<RecommendationParams>({
    principal: '1000000',
    riskTolerance: 'medium',
    strategy: 'growth',
    agentType: 'direct',
    symbols: '',
    search: '',
    industries: undefined,
    scales: undefined,
    technical_filters: {},
    promptId: undefined,
    optimizerPromptId: undefined,
    evaluationPromptId: undefined
  });

  const [prompts, setPrompts] = useState<Prompt[]>([]);
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const promptsData = await promptService.getAllPrompts();
        setPrompts(promptsData);
        if (promptsData.length > 0) {
          setFormData(prev => ({
            ...prev,
            promptId: promptsData[0].id,
            optimizerPromptId: promptsData[0].id,
            evaluationPromptId: promptsData[0].id
          }));
        }
      } catch (error) {
        console.error('プロンプト取得エラー:', error);
      }
    };

    const fetchIndustriesAndScales = async () => {
      try {
        const [industriesData, scalesData] = await Promise.all([
          axios.get('/api/industry-codes'),
          axios.get('/api/scale-codes')
        ]);
        setIndustries(industriesData.data);
        setScales(scalesData.data);
      } catch (error) {
        console.error('業種/規模データ取得エラー:', error);
      }
    };

    fetchPrompts();
    fetchIndustriesAndScales();
  }, []);

  const [isConfirming, setIsConfirming] = useState(false);
  const [candidateStocks, setCandidateStocks] = useState<Stock[]>([]);
  const [selectedStocks, setSelectedStocks] = useState<string[]>([]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name.startsWith('technical_')) {
      const filterName = name.replace('technical_', '');
      setFormData(prev => ({
        ...prev,
        technical_filters: {
          ...prev.technical_filters,
          [filterName]: ['>', value]
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    
    if (name.startsWith('technical_')) {
      const filterName = name.replace('technical_', '');
      setFormData(prev => ({
        ...prev,
        technical_filters: {
          ...prev.technical_filters,
          [filterName]: ['==', checked.toString()]
        }
      }));
    }
  };
  
  // テクニカルフィルターの更新関数
  const setTechFilter = () => {
    return formData.technical_filters || {};
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const transformedData = transformRecommendationRequest({
        ...formData,
        technical_filters: setTechFilter()
      });
      const response = await recommendationService.prepareRecommendations(transformedData);
      setCandidateStocks(response.candidate_stocks);
      setSelectedStocks(response.candidate_stocks.map((stock: Stock) => stock.symbol));
      setIsConfirming(true);
    } catch (error) {
      console.error('フィルタリングエラー:', error);
    }
  };

  const handleConfirm = () => {
    try {
      const transformedData = transformRecommendationRequest({
        ...formData,
        technical_filters: setTechFilter()
      });
      
      console.log(transformedData, selectedStocks)

      onSubmit({
        ...transformedData,
        selected_symbols: selectedStocks,
        prompt_id: formData.promptId,
        optimizer_prompt_id: formData.optimizerPromptId,
        evaluation_prompt_id: formData.evaluationPromptId
      });
      setIsConfirming(false);
    } catch (error) {
      if (error instanceof Error) {
        alert(error.message);
      } else {
        alert('リクエストの変換中にエラーが発生しました');
      }
    }
  };

  return (
    <div className="recommendation-form">
      <h2>銘柄推奨</h2>
      <form onSubmit={handleFormSubmit}>
        <div className="form-sections-container">
          <div className="form-column">
            <div className="form-section">
              <h3>投資情報</h3>
              <div className="form-group">
                <label>投資元金 (円):</label>
                <input
                  type="number"
                  name="principal"
                  value={formData.principal}
                  onChange={handleInputChange}
                  min="100000"
                  step="100000"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>リスク許容度:</label>
                <select
                  name="riskTolerance"
                  value={formData.riskTolerance}
                  onChange={handleInputChange}
                  required
                >
                  <option value="low">低リスク</option>
                  <option value="medium">中リスク</option>
                  <option value="high">高リスク</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>投資方針:</label>
                <select
                  name="strategy"
                  value={formData.strategy}
                  onChange={handleInputChange}
                  required
                >
                  <option value="growth">成長株重視</option>
                  <option value="dividend">配当株重視</option>
                  <option value="balanced">バランス型</option>
                  <option value="value">バリュー投資</option>
                </select>
              </div>
            </div>

            <div className="form-section">
              <h3>AIエージェント</h3>
          <div className="form-group agent-type-section">
            <label>AIエージェントタイプ:</label>
            <select
              name="agentType"
              value={formData.agentType}
              onChange={handleInputChange}
              required
            >
              <option value="direct">Direct (シンプルな推奨生成)</option>
              <option value="mcpagent">MCP Agent (評価・最適化ループ付き)</option>
            </select>
                <div className="form-hint">
                  MCP Agentでは、1つのLLMが推奨を生成し、別のLLMが評価とフィードバックを行います
                </div>

                {formData.agentType === 'mcpagent' && (
                  <div className="prompt-selection-group">
                    <div className="form-group">
                      <label>推奨用プロンプト:</label>
                      <select
                        name="optimizerPromptId"
                        value={formData.optimizerPromptId || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          optimizerPromptId: e.target.value ? parseInt(e.target.value) : undefined
                        })}
                        required
                      >
                        {prompts.map(prompt => (
                          <option key={prompt.id} value={prompt.id}>{prompt.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>評価用プロンプト:</label>
                      <select
                        name="evaluationPromptId"
                        value={formData.evaluationPromptId || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          evaluationPromptId: e.target.value ? parseInt(e.target.value) : undefined
                        })}
                        required
                      >
                        {prompts.map(prompt => (
                          <option key={prompt.id} value={prompt.id}>{prompt.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
              </div>

              {formData.agentType === 'direct' && (
                <div className="form-group">
                  <label>プロンプトテンプレート:</label>
                  <select
                    name="promptId"
                    value={formData.promptId || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      promptId: e.target.value ? parseInt(e.target.value) : undefined
                    })}
                    required
                  >
                    {prompts.map(prompt => (
                      <option key={prompt.id} value={prompt.id}>{prompt.name}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>

          <div className="form-column">
            <div className="form-section">
              <h3>対象銘柄</h3>
              <div className="form-group">
                <label>業種:</label>
                <select
                  name="industries"
                  multiple
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => option.value);
                    setFormData({...formData, industries: selected.length > 0 ? selected : undefined});
                  }}
                >
                  {industries.map(industry => (
                    <option key={industry.code} value={industry.code}>
                      {industry.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>規模:</label>
                <select
                  name="scales"
                  multiple
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => option.value);
                    setFormData({...formData, scales: selected.length > 0 ? selected : undefined});
                  }}
                >
                  {scales.map(scale => (
                    <option key={scale.code} value={scale.code}>
                      {scale.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>特定銘柄 (オプション, カンマ区切り):</label>
                <input
                  type="text"
                  name="symbols"
                  value={formData.symbols}
                  onChange={handleInputChange}
                  placeholder="例: 7203,9984,9432"
                />
              </div>
              
              <div className="form-group">
                <label>検索条件:</label>
                <input
                  type="text"
                  name="search"
                  value={formData.search}
                  onChange={handleInputChange}
                  placeholder="銘柄コードまたは会社名で検索"
                />
              </div>
              
              <div className="form-group">
                <h3>テクニカルフィルター</h3>
                <div className="tech-filter">
                  <div className="compact-filters">
                    <div className="filter-item">
                      <label>RSI:</label>
                      <select
                        name="technical_rsi"
                        value={formData.technical_filters?.rsi?.[1] || ''}
                        onChange={handleInputChange}
                      >
                        <option value="">指定なし</option>
                        <option value="30">30以下 (売られすぎ)</option>
                        <option value="50">50前後 (中立)</option>
                        <option value="70">70以上 (買われすぎ)</option>
                      </select>
                    </div>
                    <div className="filter-item">
                      <label>ゴールデンクロス:</label>
                      <label className="toggle-switch">
                        <input
                          type="checkbox"
                          name="technical_golden_cross"
                          checked={formData.technical_filters?.golden_cross?.[1] === 'true' || false}
                          onChange={handleCheckboxChange}
                        />
                        <span className="slider"></span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button type="submit" className="submit-btn">推奨を生成</button>
      </form>

      {isConfirming && (
          <RecommendationConfirmationDialog
            params={formData}
            stocks={candidateStocks}
            selected={selectedStocks}
            prompts={prompts}
            onSelectionChange={setSelectedStocks}
            onConfirm={handleConfirm}
            onCancel={() => setIsConfirming(false)}
          />
      )}
    </div>
  );
};

export default RecommendationForm;
