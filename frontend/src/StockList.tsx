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
    <div className="overflow-x-auto">
      <h2 className="text-xl font-bold mb-4">銘柄一覧</h2>
      <table className="min-w-full bg-white border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="py-2 px-4 border-b">シンボル</th>
            <th className="py-2 px-4 border-b">企業名</th>
            <th className="py-2 px-4 border-b">業種</th>
            <th className="py-2 px-4 border-b">ゴールデンクロス</th>
            <th className="py-2 px-4 border-b">デッドクロス</th>
            <th className="py-2 px-4 border-b">RSI</th>
            <th className="py-2 px-4 border-b">MACD</th>
            <th className="py-2 px-4 border-b">シグナル</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.symbol} className="hover:bg-gray-50">
              <td className="py-2 px-4 border-b">{stock.symbol}</td>
              <td className="py-2 px-4 border-b">{stock.name}</td>
              <td className="py-2 px-4 border-b text-left">{stock.industry}</td>
              <td className="py-2 px-4 border-b">{stock.golden_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b">{stock.dead_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b">{stock.rsi?.toFixed(2)}</td>
              <td className="py-2 px-4 border-b">{stock.macd?.toFixed(4)}</td>
              <td className="py-2 px-4 border-b">{stock.signal_line?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockList;
