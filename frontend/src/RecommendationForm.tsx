import React, { useState } from 'react';
import '../src/styles/components/RecommendationForm.css';

interface RecommendationParams {
  principal: string;
  riskTolerance: string;
  strategy: string;
  symbols: string;
}

const RecommendationForm: React.FC<{ onSubmit: (params: RecommendationParams) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<RecommendationParams>({
    principal: '1000000',
    riskTolerance: 'medium',
    strategy: 'growth',
    symbols: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
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
        
        <button type="submit" className="submit-btn">推奨を生成</button>
      </form>
    </div>
  );
};

export default RecommendationForm;
