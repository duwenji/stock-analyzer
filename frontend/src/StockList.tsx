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
import './styles/components/StockList.css';

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
  const [searchTerm, setSearchTerm] = useState<string>(''); // 検索用state
  const [sortBy, setSortBy] = useState<string>('symbol'); // ソート用state
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc'); // ソート順state

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

  const fetchStocks = async (page: number, limit: number, term: string = '', sortField: string = sortBy, order: 'asc' | 'desc' = sortOrder) => {
    try {
      const url = `http://localhost:8000/stocks?page=${page}&limit=${limit}&search=${encodeURIComponent(term)}&sort_by=${sortField}&sort_order=${order}`;
      const response = await axios.get(url);
      setStocks(response.data.stocks);
      setTotalItems(response.data.total);
      setLoading(false);
    } catch (err) {
      setError('銘柄一覧の取得に失敗しました');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks(currentPage, itemsPerPage, searchTerm, sortBy, sortOrder);
  }, [currentPage, itemsPerPage, searchTerm, sortBy, sortOrder]);
  
  // ソートハンドラ（No.列はソート対象外）
  const handleSort = (columnId: string) => {
    if (columnId === 'index') return; // No.列はソートしない
    
    if (sortBy === columnId) {
      // 同じカラムの場合はソート順をトグル
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // 新しいカラムの場合はデフォルトで昇順
      setSortBy(columnId);
      setSortOrder('asc');
    }
  };

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

  // 検索実行ハンドラ
  const handleSearch = () => {
    setCurrentPage(1); // 検索時はページを1にリセット
    fetchStocks(1, itemsPerPage, searchTerm);
  };

  // 検索リセットハンドラ
  const handleReset = () => {
    setSearchTerm('');
    setCurrentPage(1);
    fetchStocks(1, itemsPerPage, '');
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
          className={`pagination-button ${currentPage === i ? 'active' : ''}`}
        >
          {i}
        </button>
      );
    }
    
    return (
      <div className="pagination-container">
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(1)}
          className="pagination-button"
        >
          最初
        </button>
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(currentPage - 1)}
          className="pagination-button"
        >
          前へ
        </button>
        
        {pageButtons}
        
        <button
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(currentPage + 1)}
          className="pagination-button"
        >
          次へ
        </button>
        <button
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(totalPages)}
          className="pagination-button"
        >
          最後
        </button>
      </div>
    );
  };

  const ChartModal = () => {
    if (!isModalOpen || !chartImage) return null;
    
    return (
      <div className="chart-modal">
        <div className="modal-content">
          <div className="modal-header">
            <h3 className="modal-title">{selectedSymbol} チャート</h3>
            <button 
              onClick={closeModal}
              className="modal-close"
            >
              ✕
            </button>
          </div>
          <img 
            src={chartImage} 
            alt={`${selectedSymbol} チャート`} 
          />
          <div className="modal-footer">
            <button
              onClick={closeModal}
              className="modal-button"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (loading) return <div>読み込み中...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="container">
      <h2 className="text-center">銘柄一覧</h2>
      
      {/* 検索バー */}
      <div className="search-container">
        <input
          type="text"
          placeholder="銘柄コード・企業名で検索..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} className="search-button">
          検索
        </button>
        <button onClick={handleReset} className="reset-button">
          リセット
        </button>
      </div>
      
      {renderPagination()}
      
      <div className="stock-table-container">
        <table 
          {...getTableProps()} 
          className="stock-table"
        >
          <thead>
            {headerGroups.map((headerGroup: HeaderGroup<Stock>) => (
              <tr 
                {...headerGroup.getHeaderGroupProps()} 
                className="stock-table-header"
              >
                {headerGroup.headers.map((column: HeaderGroup<Stock>) => (
                  <th 
                    {...column.getHeaderProps()}
                    onClick={() => handleSort(column.id)}
                    className={column.id !== 'index' ? 'sortable-header' : ''}
                  >
                    <div className="header-cell">
                      {column.render('Header')}
                      {column.id !== 'index' && sortBy === column.id && (
                        <span className="sort-indicator">
                          {sortOrder === 'asc' ? '▲' : '▼'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {rows.map((row: Row<Stock>) => {
              prepareRow(row);
              return (
                <tr 
                  {...row.getRowProps()}
                  className="table-row"
                  onClick={() => handleRowClick(row.original.symbol)}
                >
                  {row.cells.map((cell: Cell<Stock>) => (
                    <td 
                      {...cell.getCellProps()}
                      className="table-cell"
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
