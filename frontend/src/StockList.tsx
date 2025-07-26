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

interface ApiResponse {
  stocks: Stock[];
  total: number;
  page: number;
  limit: number;
}

const StockList: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(20);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [chartImage, setChartImage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const fetchStocks = async (page: number, limit: number) => {
    try {
      console.log(`APIリクエスト開始: GET http://localhost:8000/stocks?page=${page}&limit=${limit}`);
      const response = await axios.get(`http://localhost:8000/stocks?page=${page}&limit=${limit}`);
      console.log('APIレスポンス成功:', {
        status: response.status,
        data: response.data
      });
      setStocks(response.data.stocks);
      setTotalItems(response.data.total);
      setLoading(false);
    } catch (err) {
      console.error('APIリクエストエラー:', err);
      setError('銘柄一覧の取得に失敗しました');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks(currentPage, itemsPerPage);
  }, [currentPage, itemsPerPage]);

  const handleRowClick = async (symbol: string) => {
    try {
      console.log(`チャートリクエスト開始: GET http://localhost:8000/chart/${symbol}`);
      const response = await axios.get(`http://localhost:8000/chart/${symbol}`);
      console.log('チャートレスポンス成功:', {
        status: response.status,
        data: { symbol: response.data.symbol }
      });
      setSelectedSymbol(symbol);
      setChartImage(response.data.image);
      setIsModalOpen(true);
    } catch (err) {
      console.error('チャート取得エラー:', err);
      setError('チャートの取得に失敗しました');
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setChartImage(null);
    setSelectedSymbol(null);
  };

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  if (loading) return <div>読み込み中...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  // ページネーションコントロール
  const renderPagination = () => {
    if (totalPages <= 1) return null;
    
    const pageButtons = [];
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
      pageButtons.push(
        <button
          key={i}
          onClick={() => setCurrentPage(i)}
          className={`px-3 py-1 mx-1 border rounded ${
            currentPage === i 
              ? 'bg-blue-500 text-white' 
              : 'bg-white hover:bg-gray-100'
          }`}
        >
          {i}
        </button>
      );
    }
    
    return (
      <div className="mt-4 flex justify-center">
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(1)}
          className="px-3 py-1 mx-1 border rounded disabled:opacity-50"
        >
          最初
        </button>
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(currentPage - 1)}
          className="px-3 py-1 mx-1 border rounded disabled:opacity-50"
        >
          前へ
        </button>
        
        {pageButtons}
        
        <button
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(currentPage + 1)}
          className="px-3 py-1 mx-1 border rounded disabled:opacity-50"
        >
          次へ
        </button>
        <button
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(totalPages)}
          className="px-3 py-1 mx-1 border rounded disabled:opacity-50"
        >
          最後
        </button>
      </div>
    );
  };

  // チャートモーダル
  const ChartModal = () => {
    if (!isModalOpen || !chartImage) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div className="bg-white p-4 rounded-lg max-w-3xl max-h-screen overflow-auto">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-lg font-bold">{selectedSymbol} チャート</h3>
            <button 
              onClick={closeModal}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <img 
            src={chartImage} 
            alt={`${selectedSymbol} チャート`} 
            className="max-w-full max-h-[70vh]"
          />
          <div className="mt-2 text-center">
            <button
              onClick={closeModal}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (loading) return <div>読み込み中...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="text-center">
      <h2 className="text-xl font-bold mb-4">銘柄一覧</h2>
      
      {/* ページネーションコントロール（上部） */}
      {renderPagination()}
      
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
            <tr 
              key={stock.symbol} 
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => handleRowClick(stock.symbol)}
            >
              <td className="py-2 px-4 border-b text-center">{stock.symbol}</td>
              <td className="py-2 px-4 border-b" style={{ textAlign: 'left' }}>{stock.name}</td>
              <td className="py-2 px-4 border-b" style={{ textAlign: 'left' }}>{stock.industry}</td>
              <td className="py-2 px-4 border-b text-center">{stock.golden_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b text-center">{stock.dead_cross ? "✓" : ""}</td>
              <td className="py-2 px-4 border-b text-center">
                {typeof stock.rsi === 'number' ? stock.rsi.toFixed(2) : '-'}
              </td>
              <td className="py-2 px-4 border-b text-center">
                {typeof stock.macd === 'number' ? stock.macd.toFixed(4) : '-'}
              </td>
              <td className="py-2 px-4 border-b text-center">
                {typeof stock.signal_line === 'number' ? stock.signal_line.toFixed(4) : '-'}
              </td>
            </tr>
          ))}
        </tbody>
        </table>
      </div>
      
      {/* ページネーションコントロール（下部） */}
      {renderPagination()}
      
      {/* チャートモーダル */}
      <ChartModal />
    </div>
  );
};

export default StockList;
