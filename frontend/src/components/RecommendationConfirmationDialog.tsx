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

interface Prompt {
  id: number;
  name: string;
  agent_type: string;
  system_role: string;
  user_template: string;
  output_format: string;
  created_at: string;
  updated_at: string;
}

interface RecommendationConfirmationDialogProps {
  params: {
    principal: string;
    riskTolerance: string;
    strategy: string;
    agentType: string;
    symbols: string;
    search: string;
    technical_filters?: TechnicalFilters;
    promptId?: number;
    recommendationPromptId?: number;
    evaluationPromptId?: number;
  };
  stocks: Stock[];
  selected: string[];
  prompts: Prompt[];
  onSelectionChange: (selected: string[]) => void;
  onConfirm: () => void;
  onCancel: () => void;
}

const RecommendationConfirmationDialog: React.FC<RecommendationConfirmationDialogProps> = ({
  params,
  stocks,
  selected,
  prompts,
  onSelectionChange,
  onConfirm,
  onCancel
}) => {
  const [expandedPromptId, setExpandedPromptId] = React.useState<number | null>(null);
  
  console.log('RecommendationConfirmationDialog params:', params);
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
      case 'promptId':
      case 'recommendationPromptId':
      case 'evaluationPromptId':
        if (typeof value === 'number') {
          return `ID: ${value}`;
        }
        return '指定なし';
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
    <Dialog open={true} onClose={onCancel} maxWidth="lg" fullWidth className="recommendation-confirmation-dialog">
      <DialogTitle>推奨パラメータ確認</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>入力パラメータ</Typography>
          <Grid container spacing={1}>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>投資元本:</strong> {formatParam('principal', params.principal)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>リスク許容度:</strong> {formatParam('riskTolerance', params.riskTolerance)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>投資方針:</strong> {formatParam('strategy', params.strategy)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>AIエージェント:</strong> {formatParam('agentType', params.agentType)}</Typography>
            </Grid>
              {params.agentType === 'direct' && params.promptId && (
                <>
                  <Typography variant="subtitle1" sx={{ mt: 2 }}>プロンプト:</Typography>
                  <div 
                    className="prompt-item"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (params.promptId) {
                        setExpandedPromptId(params.promptId === expandedPromptId ? null : params.promptId);
                      }
                    }}
                    style={{ 
                      border: '1px solid #ddd', 
                      borderRadius: '4px', 
                      padding: '8px', 
                      margin: '8px 0',
                      cursor: 'pointer',
                      backgroundColor: params.promptId === expandedPromptId ? '#f5f5f5' : 'white'
                    }}
                  >
                    <div className="prompt-header">
                      <Typography fontWeight="bold">
                        {prompts.find(p => p.id === params.promptId)?.name || '未選択'} ({prompts.find(p => p.id === params.promptId)?.agent_type === 'direct' ? 'Direct' : 'MCP Agent'})
                      </Typography>
                    </div>
                    {params.promptId === expandedPromptId && prompts.find(p => p.id === params.promptId) && (
                      <div className="prompt-details" style={{ marginTop: '8px' }}>
                        <div><strong>Agent Type:</strong> {prompts.find(p => p.id === params.promptId)?.agent_type}</div>
                        <div><strong>System Role:</strong> {prompts.find(p => p.id === params.promptId)?.system_role}</div>
                        <div><strong>User Template:</strong> {prompts.find(p => p.id === params.promptId)?.user_template}</div>
                        <div><strong>Output Format:</strong> {prompts.find(p => p.id === params.promptId)?.output_format}</div>
                      </div>
                    )}
                  </div>
                </>
              )}
              {params.agentType === 'mcpagent' && (
                <>
                  <Typography variant="subtitle1" sx={{ mt: 2 }}>推奨用プロンプト:</Typography>
                  <div 
                    className="prompt-item"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (params.recommendationPromptId) {
                        setExpandedPromptId(params.recommendationPromptId === expandedPromptId ? null : params.recommendationPromptId);
                      }
                    }}
                    style={{ 
                      border: '1px solid #ddd', 
                      borderRadius: '4px', 
                      padding: '8px', 
                      margin: '8px 0',
                      cursor: 'pointer',
                      backgroundColor: params.recommendationPromptId === expandedPromptId ? '#f5f5f5' : 'white'
                    }}
                  >
                    <div className="prompt-header">
                      <Typography fontWeight="bold">
                        {prompts.find(p => p.id === params.recommendationPromptId)?.name || '未選択'} ({prompts.find(p => p.id === params.recommendationPromptId)?.agent_type === 'direct' ? 'Direct' : 'MCP Agent'})
                      </Typography>
                    </div>
                    {params.recommendationPromptId === expandedPromptId && prompts.find(p => p.id === params.recommendationPromptId) && (
                      <div className="prompt-details" style={{ marginTop: '8px' }}>
                        <div><strong>Agent Type:</strong> {prompts.find(p => p.id === params.recommendationPromptId)?.agent_type}</div>
                        <div><strong>System Role:</strong> {prompts.find(p => p.id === params.recommendationPromptId)?.system_role}</div>
                        <div><strong>User Template:</strong> {prompts.find(p => p.id === params.recommendationPromptId)?.user_template}</div>
                        <div><strong>Output Format:</strong> {prompts.find(p => p.id === params.recommendationPromptId)?.output_format}</div>
                      </div>
                    )}
                  </div>
                  <Typography variant="subtitle1" sx={{ mt: 2 }}>評価用プロンプト:</Typography>
                  <div 
                    className="prompt-item"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (params.evaluationPromptId) {
                        setExpandedPromptId(params.evaluationPromptId === expandedPromptId ? null : params.evaluationPromptId);
                      }
                    }}
                    style={{ 
                      border: '1px solid #ddd', 
                      borderRadius: '4px', 
                      padding: '8px', 
                      margin: '8px 0',
                      cursor: 'pointer',
                      backgroundColor: params.evaluationPromptId === expandedPromptId ? '#f5f5f5' : 'white'
                    }}
                  >
                    <div className="prompt-header">
                      <Typography fontWeight="bold">
                        {prompts.find(p => p.id === params.evaluationPromptId)?.name || '未選択'} ({prompts.find(p => p.id === params.evaluationPromptId)?.agent_type === 'direct' ? 'Direct' : 'MCP Agent'})
                      </Typography>
                    </div>
                    {params.evaluationPromptId === expandedPromptId && prompts.find(p => p.id === params.evaluationPromptId) && (
                      <div className="prompt-details" style={{ marginTop: '8px' }}>
                        <div><strong>Agent Type:</strong> {prompts.find(p => p.id === params.evaluationPromptId)?.agent_type}</div>
                        <div><strong>System Role:</strong> {prompts.find(p => p.id === params.evaluationPromptId)?.system_role}</div>
                        <div><strong>User Template:</strong> {prompts.find(p => p.id === params.evaluationPromptId)?.user_template}</div>
                        <div><strong>Output Format:</strong> {prompts.find(p => p.id === params.evaluationPromptId)?.output_format}</div>
                      </div>
                    )}
                  </div>
                </>
              )}
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>特定銘柄:</strong> {formatParam('symbols', params.symbols)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>検索条件:</strong> {formatParam('search', params.search)}</Typography>
            </Grid>
            <Grid component="div" sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, p: 2 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>テクニカル指標:</strong> {formatParam('technical_filters', params.technical_filters)}</Typography>
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

export default RecommendationConfirmationDialog;
