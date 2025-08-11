import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Chip, Divider } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import dayjs from 'dayjs';

interface Recommendation {
  symbol: string;
  name: string;
  rating: string;
  confidence: number;
  reason: string;
  target_price?: number;
}

interface Session {
  session_id: string;
  generated_at: string;
  principal: number;
  risk_tolerance: string;
  strategy: string;
  technical_filter?: string;
}

const RecommendationDetail: React.FC = () => {
  const { session_id } = useParams<{ session_id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<Session | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);

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
        </Box>
      </Paper>

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
              <TableCell>評価</TableCell>
              <TableCell>信頼度</TableCell>
              <TableCell>目標価格</TableCell>
              <TableCell>理由</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recommendations.map((rec) => (
              <TableRow key={rec.symbol}>
                <TableCell>{rec.symbol}</TableCell>
                <TableCell>{rec.name}</TableCell>
                <TableCell>
                  <Chip 
                    label={rec.rating} 
                    color={
                      rec.rating === '強力買い' ? 'success' : 
                      rec.rating === '買い' ? 'primary' : 'default'
                    }
                  />
                </TableCell>
                <TableCell>{rec.confidence}%</TableCell>
                <TableCell>
                  {rec.target_price ? `¥${rec.target_price.toLocaleString()}` : '-'}
                </TableCell>
                <TableCell>{rec.reason}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default RecommendationDetail;
