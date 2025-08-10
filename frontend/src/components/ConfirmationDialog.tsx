import React from 'react';
import '../styles/components/ConfirmationDialog.css';

interface Stock {
  symbol: string;
  name: string;
  industry: string;
  rsi?: number;
  golden_cross?: boolean;
  indicator_date?: string;
}

interface TechnicalFilters {
  rsi?: [string, number];
  golden_cross?: [string, boolean | string];
}

interface ConfirmationDialogProps {
  params: {
    principal: string;
    riskTolerance: string;
    strategy: string;
    symbols: string;
    search: string;
    technical_filters?: TechnicalFilters;
  };
  stocks: Stock[];
  selected: string[];
  onSelectionChange: (selected: string[]) => void;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  params,
  stocks,
  selected,
  onSelectionChange,
  onConfirm,
  onCancel
}) => {
  console.log('ConfirmationDialog params:', params);
  const formatParam = (key: keyof typeof params, value: unknown): React.ReactNode => {
    if (value === null || value === undefined || value === '') {
      return '指定なし';
    }

    switch(key) {
      case 'riskTolerance':
        if (typeof value === 'string') {
          const riskMap = { low: '低リスク', medium: '中リスク', high: '高リスク' } as const;
          return riskMap[value as keyof typeof riskMap] || value;
        }
        return String(value);
      case 'strategy':
        if (typeof value === 'string') {
          const strategyMap = { 
            growth: '成長株重視', 
            dividend: '配当株重視', 
            balanced: 'バランス型',
            value: 'バリュー投資'
          } as const;
          return strategyMap[value as keyof typeof strategyMap] || value;
        }
        return String(value);
      case 'principal':
        return `${Number(value).toLocaleString()}円`;
      case 'technical_filters':
        console.log("technical_filters's value:", value);

        if (!value || typeof value !== 'object') {
          return '指定なし';
        }
        
        const filters: string[] = [];
        const techFilters = value as TechnicalFilters;
        console.log("techFilters:", techFilters);
        
        // RSIフィルターのチェック
        if (techFilters.rsi !== undefined && Array.isArray(techFilters.rsi)) {
          const [operator, val] = techFilters.rsi;
          const numVal = typeof val === 'string' ? parseFloat(val) : val;
          if (operator && typeof numVal === 'number') {
            filters.push(`RSI ${operator === '>' ? '＞' : '＜'} ${numVal}`);
          }
        }
        
        // ゴールデンクロスのチェック
        if (techFilters.golden_cross !== undefined && Array.isArray(techFilters.golden_cross)) {
          const [operator, val] = techFilters.golden_cross;
          const boolVal = typeof val === 'string' ? 
            val.toLowerCase() === 'true' : 
            Boolean(val);
          filters.push(boolVal ? 'ゴールデンクロス 有り' : 'ゴールデンクロス 無し');
        }
        
        console.log('Formatted technical_filters:', filters);
        return filters.length > 0 ? filters.join(' / ') : '指定なし';
      default:
        return String(value || '指定なし');
    }
  };

  const toggleStock = (symbol: string) => {
    const newSelected = selected.includes(symbol)
      ? selected.filter(s => s !== symbol)
      : [...selected, symbol];
    onSelectionChange(newSelected);
  };

  const toggleAllStocks = () => {
    onSelectionChange(selected.length === stocks.length ? [] : stocks.map(s => s.symbol));
  };

  return (
    <div className="confirmation-dialog-overlay">
      <div className="confirmation-dialog">
        <h3>推奨パラメータ確認</h3>
        
        <div className="param-section">
          <h4>入力パラメータ</h4>
          <div className="param-grid">
            <div>投資元本:</div>
            <div>{formatParam('principal', params.principal)}</div>
            
            <div>リスク許容度:</div>
            <div>{formatParam('riskTolerance', params.riskTolerance)}</div>
            
            <div>投資方針:</div>
            <div>{formatParam('strategy', params.strategy)}</div>
            
            <div>特定銘柄:</div>
            <div>{formatParam('symbols', params.symbols)}</div>
            
            <div>検索条件:</div>
            <div>{formatParam('search', params.search)}</div>
            
            <div>テクニカル指標:</div>
            <div>{formatParam('technical_filters', params.technical_filters)}</div>
          </div>
        </div>

        <div className="stock-section">
          <h4>候補銘柄 ({selected.length}/{stocks.length}件選択)</h4>
          <div className="stock-table-container">
            <table className="stock-table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={selected.length === stocks.length && stocks.length > 0}
                      onChange={toggleAllStocks}
                    />
                  </th>
                  <th>銘柄コード</th>
                  <th>会社名</th>
                  <th>業種</th>
                  <th>RSI</th>
                  <th>ゴールデンクロス</th>
                  <th>指標日付</th>
                </tr>
              </thead>
              <tbody>
                {stocks.map(stock => (
                  <tr key={stock.symbol}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selected.includes(stock.symbol)}
                        onChange={() => toggleStock(stock.symbol)}
                      />
                    </td>
                    <td>{stock.symbol}</td>
                    <td>{stock.name}</td>
                    <td>{stock.industry}</td>
                    <td>{typeof stock.rsi === 'number' ? stock.rsi.toFixed(2) : '-'}</td>
                    <td>{stock.golden_cross ? '○' : '-'}</td>
                    <td>{stock.indicator_date || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="action-buttons">
          <button onClick={onCancel} className="cancel-btn">キャンセル</button>
          <button 
            onClick={onConfirm} 
            className="confirm-btn"
            disabled={selected.length === 0}
          >
            推奨を生成 ({selected.length}件)
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;
