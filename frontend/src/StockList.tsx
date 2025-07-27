import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  useTable, 
  useSortBy, 
  usePagination,
  Column,
  Row,
  Cell,
  HeaderGroup
} from 'react-table';

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
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage] = useState<number>(20);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [chartImage, setChartImage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // カラム定義
  const columns: Column<Stock>[] = React.useMemo(() => [
    {
      Header: 'No.',
      id: 'index',
      accessor: (_: Stock, index: number) => (currentPage - 1) * itemsPerPage + index + 1,
      Cell: ({ value }: { value: number }) => (
        <div className="text-center">{value}</div>
      )
    },
    {
      Header: 'シンボル',
      accessor: 'symbol',
      Cell: ({ value }: { value: string }) => (
        <div className="text-center">{value}</div>
      )
    },
    {
      Header: '企業名',
      accessor: 'name',
      Cell: ({ value }: { value: string }) => (
        <div className="text-left">{value}</div>
      )
    },
    {
      Header: '業種',
      accessor: 'industry',
      Cell: ({ value }: { value: string }) => (
        <div className="text-left">{value}</div>
      )
    },
    {
      Header: 'ゴールデンクロス',
      accessor: 'golden_cross',
      Cell: ({ value }: { value?: boolean }) => (
        <div className="text-center">{value ? "✓" : ""}</div>
      )
    },
    {
      Header: 'デッドクロス',
      accessor: 'dead_cross',
      Cell: ({ value }: { value?: boolean }) => (
        <div className="text-center">{value ? "✓" : ""}</div>
      )
    },
    {
      Header: 'RSI',
      accessor: 'rsi',
      Cell: ({ value }: { value?: number }) => (
        <div className="text-center">
          {typeof value === 'number' ? value.toFixed(2) : value}
        </div>
      )
    },
    {
      Header: 'MACD',
      accessor: 'macd',
      Cell: ({ value }: { value?: number }) => (
        <div className="text-center">
          {typeof value === 'number' ? value.toFixed(4) : value}
        </div>
      )
    },
    {
      Header: 'シグナル',
      accessor: 'signal_line',
      Cell: ({ value }: { value?: number }) => (
        <div className="text-center">
          {typeof value === 'number' ? value.toFixed(4) : value}
        </div>
      )
    }
  ], [currentPage, itemsPerPage]);

  // テーブルインスタンス生成
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable<Stock>(
    { 
      columns,
      data: stocks,
      manual: true,
      pageCount: Math.ceil(totalItems / itemsPerPage),
    } as any, // 型エラー回避のため一時的にanyを使用
    useSortBy,
    usePagination
  );

  const fetchStocks = async (page: number, limit: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/stocks?page=${page}&limit=${limit}`);
      setStocks(response.data.stocks);
      setTotalItems(response.data.total);
      setLoading(false);
    } catch (err) {
      setError('銘柄一覧の取得に失敗しました');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks(currentPage, itemsPerPage);
  }, [currentPage, itemsPerPage]);

  const handleRowClick = async (symbol: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/chart/${symbol}`);
      setSelectedSymbol(symbol);
      setChartImage(response.data.image);
      setIsModalOpen(true);
    } catch (err) {
      setError('チャートの取得に失敗しました');
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setChartImage(null);
    setSelectedSymbol(null);
  };

  const totalPages = Math.ceil(totalItems / itemsPerPage);

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
          className={`px-3 py-1 mx-1 border rounded transition-colors ${
            currentPage === i 
              ? 'bg-indigo-500 text-white' 
              : 'bg-white hover:bg-indigo-50'
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
      
      {renderPagination()}
      
      <div className="inline-block overflow-x-auto w-full my-4 relative max-h-[70vh]">
        <table 
          {...getTableProps()} 
          className="bg-white border border-gray-300 w-full"
        >
          <thead>
            {headerGroups.map((headerGroup: HeaderGroup<Stock>) => (
              <tr 
                {...headerGroup.getHeaderGroupProps()} 
                className="bg-gradient-to-r from-indigo-700 to-indigo-800 text-white sticky top-0 z-10 shadow-md"
              >
                {headerGroup.headers.map((column: HeaderGroup<Stock>) => (
                  <th 
                    {...column.getHeaderProps()}
                    className="py-3 px-4 border-r border-indigo-500 cursor-pointer hover:bg-indigo-600 transition-colors"
                  >
                    <div className="flex items-center justify-center font-bold">
                      {column.render('Header')}
                      {(column as any).isSorted && (
                        <span className="ml-1 text-yellow-300">
                          {(column as any).isSortedDesc ? '▼' : '▲'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()} className="divide-y divide-gray-200">
            {rows.map((row: Row<Stock>) => {
              prepareRow(row);
              return (
                <tr 
                  {...row.getRowProps()}
                  className="hover:bg-indigo-100 cursor-pointer transition-colors duration-200"
                  onClick={() => handleRowClick(row.original.symbol)}
                >
                  {row.cells.map((cell: Cell<Stock>) => (
                    <td 
                      {...cell.getCellProps()}
                      className="py-3 px-4 border-r border-gray-300"
                    >
                      {cell.render('Cell')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      {renderPagination()}
      
      <ChartModal />
    </div>
  );
};

export default StockList;
