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
import './styles/common/common.css'; // 共通スタイルをインポート

interface Stock {
  symbol: string;
  name: string;
  industry: string;
  scale_name?: string;
  technical_date?: string;
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
  const [industryCode, setIndustryCode] = useState<string>(''); // 業種コード用state
  const [industryOptions, setIndustryOptions] = useState<{code: string, name: string}[]>([]); // 業種選択肢
  const [scaleCode, setScaleCode] = useState<string>(''); // 規模コード用state
  const [scaleOptions, setScaleOptions] = useState<{code: string, name: string}[]>([]); // 規模選択肢

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
      Header: '規模',
      accessor: 'scale_name',
      Cell: ({ value }: { value?: string }) => (
        <div className="text-left">{value || ''}</div>
      )
    },
    {
      Header: '指標日付',
      accessor: 'technical_date',
      Cell: ({ value }: { value?: string }) => (
        <div className="text-center">{value || ''}</div>
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

  const fetchStocks = async (
    page: number, 
    limit: number, 
    term: string = '', 
    industry: string = '', 
    scale: string = '',
    sortField: string = sortBy, 
    order: 'asc' | 'desc' = sortOrder
  ) => {
    try {
      const url = `/api/stocks?page=${page}&limit=${limit}&search=${encodeURIComponent(term)}&industry_code=${encodeURIComponent(industry)}&scale_code=${encodeURIComponent(scale)}&sort_by=${sortField}&sort_order=${order}`;
      const response = await axios.get(url);
      setStocks(response.data.stocks);
      setTotalItems(response.data.total);
      setLoading(false);
    } catch (err) {
      setError('銘柄一覧の取得に失敗しました');
      setLoading(false);
    }
  };

  // 業種コード一覧取得
  useEffect(() => {
    const fetchIndustryCodes = async () => {
      try {
        const response = await axios.get('/api/industry-codes');
        setIndustryOptions(response.data);
      } catch (err) {
        setError('業種コードの取得に失敗しました');
      }
    };
    fetchIndustryCodes();
  }, []);

  // 規模コード一覧取得
  useEffect(() => {
    const fetchScaleCodes = async () => {
      try {
        const response = await axios.get('/api/scale-codes');
        setScaleOptions(response.data);
      } catch (err) {
        setError('規模コードの取得に失敗しました');
      }
    };
    fetchScaleCodes();
  }, []);

  useEffect(() => {
    fetchStocks(currentPage, itemsPerPage, searchTerm, industryCode, scaleCode, sortBy, sortOrder);
  }, [currentPage, itemsPerPage, searchTerm, industryCode, scaleCode, sortBy, sortOrder]);
  
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
      const response = await axios.get(`/api/chart/${symbol}`);
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
    fetchStocks(1, itemsPerPage, searchTerm, industryCode, scaleCode);
  };

  // 検索リセットハンドラ
  const handleReset = () => {
    setSearchTerm('');
    setIndustryCode('');
    setScaleCode('');
    setCurrentPage(1);
    fetchStocks(1, itemsPerPage, '', '', '');
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
          <div className="chart-modal-content">
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
      <h2 className="text-center title-header" style={{ color: '#333', fontSize: '24px', display: 'block', backgroundColor: '#fff' }}>銘柄一覧</h2>
      
      {/* 検索バー */}
      <div className="search-container">
        <input
          type="text"
          placeholder="銘柄コード・企業名で検索..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <select
          value={industryCode}
          onChange={(e) => setIndustryCode(e.target.value)}
          className="industry-select"
        >
          <option value="">すべての業種</option>
          {industryOptions.map((option) => (
            <option key={option.code} value={option.code}>
              {option.name}
            </option>
          ))}
        </select>
        <select
          value={scaleCode}
          onChange={(e) => setScaleCode(e.target.value)}
          className="scale-select"
        >
          <option value="">すべての規模</option>
          {scaleOptions.map((option) => (
            <option key={option.code} value={option.code}>
              {option.name}
            </option>
          ))}
        </select>
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
                    className={`${column.id !== 'index' ? 'sortable-header' : ''} ${sortBy === column.id ? 'active' : ''}`}
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
