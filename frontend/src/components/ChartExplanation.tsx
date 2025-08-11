import React from 'react';
import { Tooltip } from 'react-tooltip';
import '../styles/components/ChartExplanation.css';

const ChartExplanation: React.FC = () => {
  return (
    <div className="chart-explanation">
      <h4>チャート指標の見方</h4>
      <div className="indicator-section">
        <h5>MACD指標について</h5>
        <ul>
          <li>
            <span 
              data-tooltip-id="macd-tooltip" 
              data-tooltip-content="12日EMAと26日EMAの差でトレンドの方向性を示します"
            >
              <strong>MACDライン（青）</strong>
            </span>: 短期EMAと長期EMAの差
            <Tooltip id="macd-tooltip" />
          </li>
          <li>
            <span 
              data-tooltip-id="signal-tooltip" 
              data-tooltip-content="MACDラインの9日EMAで、売買シグナルを生成します"
            >
              <strong>シグナルライン（赤）</strong>
            </span>: MACDラインの移動平均
            <Tooltip id="signal-tooltip" />
          </li>
          <li>
            <span 
              data-tooltip-id="histogram-tooltip" 
              data-tooltip-content="MACDとシグナルラインの差で、トレンドの勢いを示します"
            >
              <strong>ヒストグラム</strong>
            </span>: MACDとシグナルラインの差
            <Tooltip id="histogram-tooltip" />
            <ul>
              <li>緑: MACDがシグナルより上（強気）</li>
              <li>赤: MACDがシグナルより下（弱気）</li>
            </ul>
          </li>
          <li>
            <strong>ゴールデンクロス（▲）</strong>: 買いシグナル
          </li>
          <li>
            <strong>デッドクロス（▼）</strong>: 売りシグナル
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ChartExplanation;
