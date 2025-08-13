import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Grid
} from '@mui/material';

interface Stock {
  symbol: string;
  name: string;
  industry: string;
  rsi?: number | string | null;
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
    agentType: string;
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
      case 'agentType':
        if (typeof value === 'string') {
          const agentTypeMap = {
            direct: 'Direct (シンプルな推奨生成)',
            mcpagent: 'MCP Agent (評価・最適化ループ付き)'
          } as const;
          return agentTypeMap[value as keyof typeof agentTypeMap] || value;
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
          // 値が有効な数値かチェック
          const numVal = typeof val === 'string' ? parseFloat(val) : val;
          const isValidNumber = typeof numVal === 'number' && !isNaN(numVal);
          
          if ((operator === '>' || operator === '<') && isValidNumber) {
            filters.push(`RSI ${operator === '>' ? '＞' : '＜'} ${numVal}`);
          }
        }
        
        // ゴールデンクロスのチェック
        if (techFilters.golden_cross !== undefined && Array.isArray(techFilters.golden_cross)) {
          const val = techFilters.golden_cross[1]; // 2番目の要素のみ取得
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
    <Dialog open={true} onClose={onCancel} maxWidth="lg" fullWidth>
      <DialogTitle>推奨パラメータ確認</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>入力パラメータ</Typography>
          <Grid container spacing={2}>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">投資元本:</Typography>
              <Typography>{formatParam('principal', params.principal)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">リスク許容度:</Typography>
              <Typography>{formatParam('riskTolerance', params.riskTolerance)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">投資方針:</Typography>
              <Typography>{formatParam('strategy', params.strategy)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">AIエージェントタイプ:</Typography>
              <Typography>{formatParam('agentType', params.agentType)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">特定銘柄:</Typography>
              <Typography>{formatParam('symbols', params.symbols)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">検索条件:</Typography>
              <Typography>{formatParam('search', params.search)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="subtitle1">テクニカル指標:</Typography>
              <Typography>{formatParam('technical_filters', params.technical_filters)}</Typography>
            </Grid>
          </Grid>
        </Box>

        <Box>
          <Typography variant="h6" gutterBottom>
            候補銘柄 ({selected.length}/{stocks.length}件選択)
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <Checkbox
                      checked={selected.length === stocks.length && stocks.length > 0}
                      onChange={toggleAllStocks}
                    />
                  </TableCell>
                  <TableCell>銘柄コード</TableCell>
                  <TableCell>会社名</TableCell>
                  <TableCell>業種</TableCell>
                  <TableCell>RSI</TableCell>
                  <TableCell>ゴールデンクロス</TableCell>
                  <TableCell>指標日付</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {stocks.map(stock => (
                  <TableRow key={stock.symbol}>
                    <TableCell>
                      <Checkbox
                        checked={selected.includes(stock.symbol)}
                        onChange={() => toggleStock(stock.symbol)}
                      />
                    </TableCell>
                    <TableCell>{stock.symbol}</TableCell>
                    <TableCell>{stock.name}</TableCell>
                    <TableCell>{stock.industry}</TableCell>
                    <TableCell>{
                      stock.rsi === null || stock.rsi === undefined ? '-' : 
                      typeof stock.rsi === 'number' ? stock.rsi.toFixed(2) :
                      stock.rsi.toString().replace(/^Decimal\(['"]?|['"]?\)$/g, '')
                    }</TableCell>
                    <TableCell>{stock.golden_cross ? '○' : '-'}</TableCell>
                    <TableCell>{stock.indicator_date || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} variant="outlined">キャンセル</Button>
        <Button 
          onClick={onConfirm} 
          variant="contained"
          disabled={selected.length === 0}
        >
          推奨を生成 ({selected.length}件)
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;
