import React, { useState } from 'react';
import '../src/styles/components/RecommendationForm.css';

interface RecommendationParams {
  principal: string;
  riskTolerance: string;
  strategy: string;
  symbols: string;
  search: string;
  technical_filters?: {
    [key: string]: [string, any];
  };
}

const RecommendationForm: React.FC<{ onSubmit: (params: RecommendationParams) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<RecommendationParams>({
    principal: '1000000',
    riskTolerance: 'medium',
    strategy: 'growth',
    symbols: '',
    search: ''
  });
  
  // テクニカルフィルターの状態管理
  const [rsiOperator, setRsiOperator] = useState<string>('');
  const [rsiValue, setRsiValue] = useState<string>('');
  const [goldenCross, setGoldenCross] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // テクニカルフィルターの更新関数
  const setTechFilter = () => {
    const filters: {[key: string]: [string, any]} = {};
    
    if (rsiOperator && rsiValue) {
      filters['rsi'] = [rsiOperator, parseFloat(rsiValue)];
    }
    
    if (goldenCross) {
      filters['golden_cross'] = ['==', 'true'];
    }
    
    return filters;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = {
      ...formData,
      technical_filters: setTechFilter()
    };
    onSubmit(params);
  };

  return (
    <div className="recommendation-form">
      <h2>銘柄推奨パラメータ</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>投資元金 (円):</label>
          <input
            type="number"
            name="principal"
            value={formData.principal}
            onChange={handleChange}
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
            onChange={handleChange}
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
            onChange={handleChange}
            required
          >
            <option value="growth">成長株重視</option>
            <option value="dividend">配当株重視</option>
            <option value="balanced">バランス型</option>
            <option value="value">バリュー投資</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>特定銘柄 (オプション, カンマ区切り):</label>
          <input
            type="text"
            name="symbols"
            value={formData.symbols}
            onChange={handleChange}
            placeholder="例: 7203,9984,9432"
          />
        </div>
        
        <div className="form-group">
          <label>検索条件:</label>
          <input
            type="text"
            name="search"
            value={formData.search}
            onChange={handleChange}
            placeholder="銘柄コードまたは会社名で検索"
          />
        </div>
        
        <div className="form-group">
          <h3>テクニカルフィルター</h3>
          <div className="tech-filter">
            <div>
              <label>RSI: </label>
              <select 
                value={rsiOperator}
                onChange={(e) => setRsiOperator(e.target.value)}
              >
                <option value="">選択</option>
                <option value="<">以下</option>
                <option value=">">以上</option>
              </select>
              <input 
                type="number" 
                min="0" 
                max="100"
                value={rsiValue}
                onChange={(e) => setRsiValue(e.target.value)}
                placeholder="値"
              />
            </div>
            <div>
              <label>ゴールデンクロス: </label>
              <input 
                type="checkbox"
                checked={goldenCross}
                onChange={(e) => setGoldenCross(e.target.checked)}
              />
            </div>
          </div>
        </div>
        
        <button type="submit" className="submit-btn">推奨を生成</button>
      </form>
    </div>
  );
};

export default RecommendationForm;
