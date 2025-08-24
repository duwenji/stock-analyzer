import React, { useState } from 'react';
import '../src/styles/components/RecommendationResults.css';
import { chartService } from './utils/apiService';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Box
} from '@mui/material';

interface Recommendation {
  symbol: string;
  name: string;
  confidence: number;
  allocation: string;
  reason: string;
}

interface ApiResponse {
  recommendations: Recommendation[];
  total_return_estimate: string;
  ai_raw_response?: string;
}

const RecommendationResults: React.FC<{ data: ApiResponse | null }> = ({ data }) => {
  const [showRawResponse, setShowRawResponse] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [chartImage, setChartImage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [loadingChart, setLoadingChart] = useState<boolean>(false);

  if (!data || !data.recommendations) {
    return (
      <div className="recommendation-results">
        <h3>推奨結果</h3>
        <p>推奨結果がありません。パラメータを調整して再実行してください。</p>
      </div>
    );
  }

  const formatJson = (jsonString: string): string => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch (e) {
      return jsonString;
    }
  };

  const handleRowClick = async (symbol: string) => {
    try {
      setLoadingChart(true);
      setSelectedSymbol(symbol);
      const response = await chartService.getChart(symbol);
      setChartImage(response.image);
      setIsModalOpen(true);
    } catch (err) {
      console.error('チャートの取得に失敗しました:', err);
    } finally {
      setLoadingChart(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setChartImage(null);
    setSelectedSymbol(null);
  };

  return (
    <div className="recommendation-results">
      <h3>AI推奨銘柄</h3>
      <div className="summary">
        <p className="return-estimate">
          期待リターン: <strong>{data.total_return_estimate}</strong>
        </p>
      </div>
      
      <div className="allocation-chart">
        {data.recommendations.map((item, index) => (
          <div 
            key={index} 
            className="allocation-bar"
            style={{ width: `${parseFloat(item.allocation)}%` }}
          >
            <span className="symbol">{item.symbol}</span>
            <span className="percentage">{item.allocation}</span>
          </div>
        ))}
      </div>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>銘柄コード</th>
              <th>会社名</th>
              <th>信頼度</th>
              <th>推奨割合</th>
              <th>理由</th>
            </tr>
          </thead>
          <tbody>
            {data.recommendations.map((item, index) => (
              <tr 
                key={index}
                onClick={() => handleRowClick(item.symbol)}
                style={{ cursor: 'pointer' }}
              >
                <td>{item.symbol}</td>
                <td>{item.name}</td>
                <td>
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${item.confidence}%` }}
                    >
                      {item.confidence}%
                    </div>
                  </div>
                </td>
                <td>{item.allocation}</td>
                <td className="reason">{item.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.ai_raw_response && (
        <div className="raw-response-section">
          <button 
            className="toggle-raw-response"
            onClick={() => setShowRawResponse(!showRawResponse)}
          >
            {showRawResponse ? 'AI生レスポンスを隠す' : 'AI生レスポンスを表示'}
          </button>
          
          {showRawResponse && (
            <div className="raw-response-content">
              <h4>AIからの生レスポンス</h4>
              <pre className="formatted-json">
                {formatJson(data.ai_raw_response)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* チャートモーダル */}
      <Dialog 
        open={isModalOpen} 
        onClose={closeModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSymbol} チャート
        </DialogTitle>
        <DialogContent>
          {loadingChart ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : chartImage ? (
            <img 
              src={chartImage} 
              alt={`${selectedSymbol} チャート`}
              style={{ width: '100%' }}
            />
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeModal}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default RecommendationResults;
