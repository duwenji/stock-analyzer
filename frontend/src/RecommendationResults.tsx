import React from 'react';
import '../src/styles/components/RecommendationResults.css';

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
}

const RecommendationResults: React.FC<{ data: ApiResponse | null }> = ({ data }) => {
  if (!data || !data.recommendations) {
    return (
      <div className="recommendation-results">
        <h3>推奨結果</h3>
        <p>推奨結果がありません。パラメータを調整して再実行してください。</p>
      </div>
    );
  }

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
            <span className="percentage">{item.allocation}%</span>
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
              <tr key={index}>
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
    </div>
  );
};

export default RecommendationResults;
