import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Stock {
  symbol: string;
  name: string;
  industry: string;
  golden_cross?: boolean;
  dead_cross?: boolean;
  rsi?: number;
  macd?: number;
  signal_line?: number;
}

const StockList: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        console.log('APIリクエスト開始: GET http://localhost:8000/stocks');
        const response = await axios.get('http://localhost:8000/stocks');
        console.log('APIレスポンス成功:', {
          status: response.status,
          data: response.data.slice(0, 3) // 最初の3件をログ出力
        });
        setStocks(response.data);
        setLoading(false);
      } catch (err) {
        console.error('APIリクエストエラー:', err);
        setError('銘柄一覧の取得に失敗しました');
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  if (loading) return <div>読み込み中...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="text-center">
      <h2 className="text-xl font-bold mb-4">銘柄一覧</h2>
      <div className="inline-block overflow-x-auto">
        <table className="bg-white border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="py-2 px-4 border-b text-center">シンボル</th>
            <th className="py-2 px-4 border-b text-center" style={{ textAlign: 'left' }}>企業名</th>
            <th className="py-2 px-4 border-b text-center" style={{ textAlign: 'left' }}>業種</th>
            <th className="py-2 px-4 border-b text-center">ゴールデンクロス</th>
            <th className="py-2 px-4 border-b text-center">デッドクロス</th>
            <th className="py-2 px-4 border-b text-center">RSI</th>
            <th className="py-2 px-4 border-b text-center">MACD</th>
            <th className="py-2 px-4 border-b text-center">シグナル</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.symbol} className="hover:bg-gray-50">
              <td className="py-2 px-4 border-b text-center">{stock.symbol}</td>
              <td className="py-2 px-4 border-b" style={{ textAlign: 'left' }}>{stock.name}</td>
              <td className="py-2 px-4 border-b" style={{ textAlign: 'left' }}>{stock.industry}</td>
              <td className="py-2 px-4 border-b text-center">{stock.golden_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b text-center">{stock.dead_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b text-center">{stock.rsi?.toFixed(2)}</td>
              <td className="py-2 px-4 border-b text-center">{stock.macd?.toFixed(4)}</td>
              <td className="py-2 px-4 border-b text-center">{stock.signal_line?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>
    </div>
  );
};

export default StockList;
