import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { stockService, chartService } from './utils/apiService';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TableSortLabel,
  TablePagination,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Alert,
  Typography
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

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
  const columns = [
    { id: 'index', label: 'No.', align: 'center', sortable: false },
    { id: 'symbol', label: 'シンボル', align: 'center', sortable: true },
    { id: 'name', label: '企業名', align: 'left', sortable: true },
    { id: 'industry', label: '業種', align: 'left', sortable: true },
    { id: 'scale_name', label: '規模', align: 'left', sortable: true },
    { id: 'technical_date', label: '指標日付', align: 'center', sortable: true },
    { id: 'golden_cross', label: 'ゴールデンクロス', align: 'center', sortable: true },
    { id: 'dead_cross', label: 'デッドクロス', align: 'center', sortable: true },
    { id: 'rsi', label: 'RSI', align: 'center', sortable: true },
    { id: 'macd', label: 'MACD', align: 'center', sortable: true },
    { id: 'signal_line', label: 'シグナル', align: 'center', sortable: true }
  ];

  // 行データのフォーマット
  const formatRowData = (stock: Stock, index: number) => ({
    index: (currentPage - 1) * itemsPerPage + index + 1,
    symbol: stock.symbol,
    name: stock.name,
    industry: stock.industry,
    scale_name: stock.scale_name || '',
    technical_date: stock.technical_date || '',
    golden_cross: stock.golden_cross ? "✓" : "",
    dead_cross: stock.dead_cross ? "✓" : "",
    rsi: typeof stock.rsi === 'number' ? stock.rsi.toFixed(2) : stock.rsi,
    macd: typeof stock.macd === 'number' ? stock.macd.toFixed(4) : stock.macd,
    signal_line: typeof stock.signal_line === 'number' ? stock.signal_line.toFixed(4) : stock.signal_line
  });

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
      const params = {
        page,
        limit,
        search: term,
        industry_code: industry,
        scale_code: scale,
        sort_by: sortField,
        sort_order: order
      };
      const response = await stockService.getStocks(params);
      setStocks(response.stocks);
      setTotalItems(response.total);
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
        const response = await stockService.getIndustryCodes();
        setIndustryOptions(response);
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
        const response = await stockService.getScaleCodes();
        setScaleOptions(response);
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
      const response = await chartService.getChart(symbol);
      setSelectedSymbol(symbol);
      setChartImage(response.image);
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

  const ChartModal = () => {
    if (!isModalOpen || !chartImage) return null;
    
    return (
      <Dialog 
        open={isModalOpen} 
        onClose={closeModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSymbol} チャート
          <IconButton
            onClick={closeModal}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <img 
            src={chartImage} 
            alt={`${selectedSymbol} チャート`}
            style={{ width: '100%' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeModal}>閉じる</Button>
        </DialogActions>
      </Dialog>
    );
  };

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
      <CircularProgress />
    </Box>
  );
  if (error) return (
    <Alert severity="error" sx={{ m: 2 }}>
      {error}
    </Alert>
  );

  return (
    <div className="container">
      <h2 className="text-center title-header" style={{ color: '#333', fontSize: '24px', display: 'block', backgroundColor: '#fff' }}>銘柄一覧</h2>
      
      {/* 検索バー */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
        <TextField
          label="銘柄コード・企業名で検索"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          sx={{ flex: 2 }}
        />
        
        <FormControl size="small" sx={{ flex: 1 }}>
          <InputLabel>業種</InputLabel>
          <Select
            value={industryCode}
            onChange={(e) => setIndustryCode(e.target.value)}
            label="業種"
          >
            <MenuItem value="">すべての業種</MenuItem>
            {industryOptions.map((option) => (
              <MenuItem key={option.code} value={option.code}>
                {option.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl size="small" sx={{ flex: 1 }}>
          <InputLabel>規模</InputLabel>
          <Select
            value={scaleCode}
            onChange={(e) => setScaleCode(e.target.value)}
            label="規模"
          >
            <MenuItem value="">すべての規模</MenuItem>
            {scaleOptions.map((option) => (
              <MenuItem key={option.code} value={option.code}>
                {option.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Button 
          variant="contained" 
          onClick={handleSearch}
          sx={{ height: 40 }}
        >
          検索
        </Button>
        <Button 
          variant="outlined" 
          onClick={handleReset}
          sx={{ height: 40 }}
        >
          リセット
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, my: 2 }}>
        <TablePagination
          component="div"
          count={totalItems}
          page={currentPage - 1}
          onPageChange={(_, newPage) => setCurrentPage(newPage + 1)}
          rowsPerPage={itemsPerPage}
          rowsPerPageOptions={[20]}
          sx={{ my: 0 }}
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} / ${count}`}
        />
        <TextField
          label="ページ指定"
          type="number"
          size="small"
          value={currentPage}
          onChange={(e) => {
            const page = parseInt(e.target.value);
            if (!isNaN(page) && page >= 1 && page <= Math.ceil(totalItems / itemsPerPage)) {
              setCurrentPage(page);
            }
          }}
          sx={{ width: 100 }}
          inputProps={{
            min: 1,
            max: Math.ceil(totalItems / itemsPerPage)
          }}
        />
        <Typography variant="body2">
          全{Math.ceil(totalItems / itemsPerPage)}ページ
        </Typography>
      </Box>

      <TableContainer component={Paper} sx={{ mb: 2, width: '100%', overflowX: 'auto' }}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align as any}
                  sx={{ 
                    fontWeight: 'bold',
                    cursor: column.sortable ? 'pointer' : 'default'
                  }}
                  onClick={() => column.sortable && handleSort(column.id)}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={sortBy === column.id}
                      direction={sortOrder}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {stocks.map((stock, index) => (
              <TableRow 
                hover 
                key={`${stock.symbol}-${index}`}
                onClick={() => handleRowClick(stock.symbol)}
                sx={{ '&:hover': { cursor: 'pointer' } }}
              >
                {Object.entries(formatRowData(stock, index)).map(([key, value]) => (
                  <TableCell 
                    key={key}
                    align={columns.find(c => c.id === key)?.align as any}
                  >
                    {value}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <ChartModal />
    </div>
  );
};

export default StockList;
