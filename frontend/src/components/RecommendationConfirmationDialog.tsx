import React from 'react';
import { stockService } from '../utils/apiService';
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
  Box
} from '@mui/material';

interface Stock {
  symbol: string;
  name: string;
  industry: string;
  industry_name_33?: string;
  scale_name?: string;
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
    industries?: string[];
    scales?: string[];
    technical_filters?: TechnicalFilters;
    promptId?: number;
    optimizerPromptId?: number;
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
  const [industryMap, setIndustryMap] = React.useState<Record<string, string>>({});
  const [scaleMap, setScaleMap] = React.useState<Record<string, string>>({});

  // 業種と規模のマッピングデータを取得
  React.useEffect(() => {
    const fetchMappings = async () => {
      try {
        const industries = await stockService.getIndustryCodes();
        setIndustryMap(Object.fromEntries(
          industries.map(item => [item.code, item.name])
        ));
        
        const scales = await stockService.getScaleCodes();
        setScaleMap(Object.fromEntries(
          scales.map(item => [item.code, item.name])
        ));
      } catch (error) {
        console.error('マッピングデータ取得エラー:', error);
      }
    };
    
    fetchMappings();
  }, []);
  
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
      case 'optimizerPromptId':
      case 'evaluationPromptId':
        if (typeof value === 'number') {
          return `ID: ${value}`;
        }
        return '指定なし';
      case 'technical_filters':
        if (!value || typeof value !== 'object') {
          return '指定なし';
        }
        
        const filters: string[] = [];
        const techFilters = value as TechnicalFilters;
        
        // RSIフィルターのチェック
        if (techFilters.rsi && Array.isArray(techFilters.rsi)) {
          const [operator, val] = techFilters.rsi;
          const numVal = typeof val === 'string' ? parseFloat(val) : val;
          if (typeof numVal === 'number' && !isNaN(numVal)) {
            filters.push(`RSI ${operator === '>' ? '＞' : '＜'} ${numVal}`);
          }
        }
        
        // ゴールデンクロスのチェック
        if (techFilters.golden_cross && Array.isArray(techFilters.golden_cross)) {
          const val = techFilters.golden_cross[1];
          if (typeof val === 'boolean' || typeof val === 'string') {
            const boolVal = typeof val === 'string' ? val.toLowerCase() === 'true' : val;
            filters.push(boolVal ? 'ゴールデンクロス 有り' : 'ゴールデンクロス 無し');
          }
        }
        
        return filters.length > 0 ? filters.join(' / ') : '指定なし';
        
      case 'industries':
        return Array.isArray(value) && value.length > 0 
          ? value.map(code => industryMap[code] || code).join(', ') 
          : '指定なし';
          
      case 'scales':
        return Array.isArray(value) && value.length > 0 
          ? value.map(code => scaleMap[code] || code).join(', ') 
          : '指定なし';
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
          <div className="form-sections-container">
            {/* 左カラム - 投資情報 & AIエージェント */}
            <div className="form-column">
              <div className="form-section">
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>投資情報</Typography>
                <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>投資元本:</strong> {formatParam('principal', params.principal)}</Typography>
                <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>リスク許容度:</strong> {formatParam('riskTolerance', params.riskTolerance)}</Typography>
                <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>投資方針:</strong> {formatParam('strategy', params.strategy)}</Typography>
              </div>

              <div className="form-section">
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>AIエージェント</Typography>
                <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>AIエージェント:</strong> {formatParam('agentType', params.agentType)}</Typography>
                {params.agentType === 'direct' && params.promptId && (
                  <div className="form-subsection">
                    <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>プロンプト:</Typography>
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
                  </div>
                )}
                {params.agentType === 'mcpagent' && (
                  <div className="form-subsection">
                    <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>推奨用プロンプト:</Typography>
                    <div 
                      className="prompt-item"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (params.optimizerPromptId) {
                          setExpandedPromptId(params.optimizerPromptId === expandedPromptId ? null : params.optimizerPromptId);
                        }
                      }}
                      style={{ 
                        border: '1px solid #ddd', 
                        borderRadius: '4px', 
                        padding: '8px', 
                        margin: '8px 0',
                        cursor: 'pointer',
                        backgroundColor: params.optimizerPromptId === expandedPromptId ? '#f5f5f5' : 'white'
                      }}
                    >
                      <div className="prompt-header">
                        <Typography fontWeight="bold">
                          {prompts.find(p => p.id === params.optimizerPromptId)?.name || '未選択'} ({prompts.find(p => p.id === params.optimizerPromptId)?.agent_type === 'direct' ? 'Direct' : 'MCP Agent'})
                        </Typography>
                      </div>
                      {params.optimizerPromptId === expandedPromptId && prompts.find(p => p.id === params.optimizerPromptId) && (
                        <div className="prompt-details" style={{ marginTop: '8px' }}>
                          <div><strong>Agent Type:</strong> {prompts.find(p => p.id === params.optimizerPromptId)?.agent_type}</div>
                          <div><strong>System Role:</strong> {prompts.find(p => p.id === params.optimizerPromptId)?.system_role}</div>
                          <div><strong>User Template:</strong> {prompts.find(p => p.id === params.optimizerPromptId)?.user_template}</div>
                          <div><strong>Output Format:</strong> {prompts.find(p => p.id === params.optimizerPromptId)?.output_format}</div>
                        </div>
                      )}
                    </div>
                    <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>評価用プロンプト:</Typography>
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
                  </div>
                )}
              </div>
              
              {/* 右カラム - 対象銘柄 & テクニカルフィルター */}
              <div className="form-column">
                <div className="form-section">
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>対象銘柄</Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>特定銘柄:</strong> {formatParam('symbols', params.symbols)}</Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>検索条件:</strong> {formatParam('search', params.search)}</Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5, mb: 1 }}><strong>業種:</strong> {formatParam('industries', params.industries)}</Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>規模:</strong> {formatParam('scales', params.scales)}</Typography>
                </div>
                
                <div className="form-section">
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>テクニカルフィルター</Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}><strong>テクニカル指標:</strong> {formatParam('technical_filters', params.technical_filters)}</Typography>
                </div>
              </div>
            </div>
          </div>
        </Box>

        {stocks.length > 0 ? (
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
                    <TableCell>業種(33分類)</TableCell>
                    <TableCell>規模</TableCell>
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
                      <TableCell>{stock.industry_name_33 || stock.industry || '-'}</TableCell>
                      <TableCell>{stock.scale_name || '-'}</TableCell>
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
        ) : (
          <Box sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="body1" color="text.secondary">
              対象銘柄が指定されていないため、全銘柄から推奨します
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} variant="outlined">キャンセル</Button>
        <Button 
          onClick={onConfirm} 
          variant="contained"
        >
          推奨を生成 ({selected.length}件)
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RecommendationConfirmationDialog;
