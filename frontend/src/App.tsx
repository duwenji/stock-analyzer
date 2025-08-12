import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import 'dayjs/locale/ja';
import dayjs from 'dayjs';
import StockList from './StockList';
import RecommendationForm from './RecommendationForm';
import RecommendationResults from './RecommendationResults';
import RecommendationHistory from './RecommendationHistory';
import RecommendationDetail from './RecommendationDetail';
import './styles/common/common.css';

dayjs.locale('ja');

const defaultTheme = createTheme();

function App() {
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
        selected_symbols: params.selected_symbols,
        agent_type: params.agent_type || "direct"
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
    <ThemeProvider theme={defaultTheme}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Router>
        <div className="App">
          <header className="App-header">
            <h1 className="text-xl font-bold py-4">株式分析システム</h1>
            <nav className="tabs p-4 max-w-4xl mx-auto">
              <Link to="/" className="tab-button">銘柄一覧</Link>
              <Link to="/recommend" className="tab-button">AI銘柄推奨</Link>
              <Link to="/history" className="tab-button">推奨履歴</Link>
            </nav>
          </header>
          
          <main className="p-4 max-w-4xl mx-auto">
            <Routes>
              <Route path="/" element={<StockList />} />
              <Route path="/recommend" element={
                <div className="recommendation-container">
                  <RecommendationForm onSubmit={handleRecommendationSubmit} />
                  {isLoading && <div className="loading">推奨を生成中...</div>}
                  {error && <div className="error">{error}</div>}
                  <RecommendationResults data={recommendationData} />
                </div>
              } />
              <Route path="/history" element={<RecommendationHistory />} />
              <Route path="/recommendations/:session_id" element={<RecommendationDetail />} />
            </Routes>
          </main>
        </div>
        </Router>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

export default App;
