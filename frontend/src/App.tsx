import React, { useState } from 'react';
import StockList from './StockList';
import RecommendationForm from './RecommendationForm';
import RecommendationResults from './RecommendationResults';
import './styles/common/common.css';

function App() {
  const [activeTab, setActiveTab] = useState<'list' | 'recommend'>('list');
  const [recommendationData, setRecommendationData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRecommendationSubmit = async (params: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log("params: ", params)

      const requestData = {
        principal: parseFloat(params.principal),
        risk_tolerance: params.risk_tolerance,
        strategy: params.strategy,
        technical_filters: params.technical_filters,
        symbols: params.symbols,
        selected_symbols: params.selected_symbols
      };
      console.log("requestData:", requestData)
      
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        throw new Error(`APIエラー: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("API response data:", JSON.stringify(data, null, 2));
      setRecommendationData(data);
    } catch (err) {
      setError('推奨生成中にエラーが発生しました。詳細はコンソールを確認してください。');
      console.error('推奨生成エラー:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="text-xl font-bold py-4">株式分析システム</h1>
      </header>
      
      <div className="tabs p-4 max-w-4xl mx-auto">
        <button 
          className={`tab-button ${activeTab === 'list' ? 'active' : ''}`}
          onClick={() => setActiveTab('list')}
        >
          銘柄一覧
        </button>
        <button 
          className={`tab-button ${activeTab === 'recommend' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommend')}
        >
          AI銘柄推奨
        </button>
      </div>
      
      <main className="p-4 max-w-4xl mx-auto">
        {activeTab === 'list' ? (
          <StockList />
        ) : (
          <div className="recommendation-container">
            <RecommendationForm onSubmit={handleRecommendationSubmit} />
            
            {isLoading && <div className="loading">推奨を生成中...</div>}
            {error && <div className="error">{error}</div>}
            
            <RecommendationResults data={recommendationData} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
