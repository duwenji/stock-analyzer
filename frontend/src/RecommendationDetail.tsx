import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Button, 
  Chip, 
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import dayjs from 'dayjs';
import { chartService } from './utils/apiService';

interface Recommendation {
  symbol: string;
  name: string;
  confidence: number;
  allocation: number;
  reason: string;
}

interface Session {
  session_id: string;
  generated_at: string;
  principal: number;
  risk_tolerance: string;
  strategy: string;
  technical_filter?: string;
  ai_raw_response?: string;
  total_return_estimate?: string;
}

const RecommendationDetail: React.FC = () => {
  const { session_id } = useParams<{ session_id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [chartImage, setChartImage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [loadingChart, setLoadingChart] = useState<boolean>(false);

  useEffect(() => {
    const fetchRecommendationDetail = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/recommendations/${session_id}`);
        const data = await response.json();
        setSession(data.session);
        setRecommendations(data.recommendations);
      } catch (error) {
        console.error('推奨詳細の取得に失敗しました:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendationDetail();
  }, [session_id]);

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">読み込み中...</Typography>
      </Box>
    );
  }

  if (!session) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">セッション情報が見つかりません</Typography>
      </Box>
    );
  }

  const handleRowClick = async (symbol: string) => {
    try {
      setLoadingChart(true);
      setSelectedSymbol(symbol);
      const response = await chartService.getChart(symbol);
      setChartImage(response.image);
      setIsModalOpen(true);
    } catch (err) {
      console.error('チャートの取得に失敗しました:', err);
    } finally {
      setLoadingChart(false);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setChartImage(null);
    setSelectedSymbol(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Button 
        startIcon={<ArrowBack />}
        onClick={() => navigate(-1)}
        sx={{ mb: 2 }}
      >
        戻る
      </Button>

      <Typography variant="h4" gutterBottom>
        推奨詳細
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ 
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          '& > div': {
            minWidth: 0
          }
        }}>
          <Box>
            <Typography variant="subtitle1">セッションID</Typography>
            <Typography>{session.session_id}</Typography>
          </Box>
          <Box>
            <Typography variant="subtitle1">生成日時</Typography>
            <Typography>{dayjs(session.generated_at).format('YYYY/MM/DD HH:mm')}</Typography>
          </Box>
          <Box sx={{ 
            gridColumn: { xs: '1', md: '1' },
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }
          }}>
            <Box>
              <Typography variant="subtitle1">元本</Typography>
              <Typography>¥{session.principal.toLocaleString()}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle1">リスク許容度</Typography>
              <Chip 
                label={session.risk_tolerance} 
                color={
                  session.risk_tolerance === '高' ? 'error' : 
                  session.risk_tolerance === '中' ? 'warning' : 'success'
                }
              />
            </Box>
            <Box>
              <Typography variant="subtitle1">戦略</Typography>
              <Typography>{session.strategy}</Typography>
            </Box>
          </Box>
          {session.technical_filter && (
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Typography variant="subtitle1">テクニカルフィルタ</Typography>
              <Typography>{session.technical_filter}</Typography>
            </Box>
          )}
          {session.total_return_estimate && (
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Typography variant="subtitle1">期待リターン見積もり</Typography>
              <Typography variant="body1" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {session.total_return_estimate}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {session.ai_raw_response && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            AI生レスポンス
          </Typography>
          <Box
            sx={{
              p: 2,
              backgroundColor: 'grey.100',
              borderRadius: 1,
              maxHeight: '300px',
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              whiteSpace: 'pre-wrap'
            }}
          >
            {session.ai_raw_response}
          </Box>
        </Paper>
      )}

      <Divider sx={{ my: 3 }} />

      <Typography variant="h5" gutterBottom>
        推奨銘柄 ({recommendations.length}件)
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>銘柄コード</TableCell>
              <TableCell>銘柄名</TableCell>
              <TableCell>推奨割合</TableCell>
              <TableCell>信頼度</TableCell>
              <TableCell>理由</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recommendations.map((rec) => (
              <TableRow 
                key={rec.symbol}
                onClick={() => handleRowClick(rec.symbol)}
                sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
              >
                <TableCell>{rec.symbol}</TableCell>
                <TableCell>{rec.name}</TableCell>
                <TableCell>
                  <Chip 
                    label={`${rec.allocation}`} 
                  />
                </TableCell>
                <TableCell>{rec.confidence}%</TableCell>
                <TableCell>{rec.reason}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* チャートモーダル */}
      <Dialog 
        open={isModalOpen} 
        onClose={closeModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSymbol} チャート
        </DialogTitle>
        <DialogContent>
          {loadingChart ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : chartImage ? (
            <img 
              src={chartImage} 
              alt={`${selectedSymbol} チャート`}
              style={{ width: '100%' }}
            />
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeModal}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RecommendationDetail;
