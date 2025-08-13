import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TablePagination, TextField, MenuItem, Select, FormControl, InputLabel, Typography, Box, Tooltip, TextFieldProps } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import dayjs, { Dayjs } from 'dayjs';
import { styled } from '@mui/system';

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    cursor: 'pointer'
  },
}));

interface Session {
  session_id: string;
  generated_at: string;
  principal: number;
  risk_tolerance: string;
  strategy: string;
  technical_filter?: string;
  symbol_count: number;
  prompt_name?: string;
}

const RecommendationHistory: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sort, setSort] = useState('generated_at-desc');
  const [startDate, setStartDate] = useState<Dayjs | null>(null);
  const [endDate, setEndDate] = useState<Dayjs | null>(null);
  const [strategyFilter, setStrategyFilter] = useState('');
  const navigate = useNavigate();

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        limit: rowsPerPage.toString(),
        sort,
        ...(startDate && { start_date: startDate.format('YYYY-MM-DD') }),
        ...(endDate && { end_date: endDate.format('YYYY-MM-DD') }),
        ...(strategyFilter && { strategy: strategyFilter })
      });

      const response = await fetch(`/api/recommendations/history?${params}`);
      if (!response.ok) {
        throw new Error('推奨履歴の取得に失敗しました');
      }
      const data = await response.json();
      // バックエンドから空配列が返るように修正したため、安全にアクセス
      setSessions(data.sessions || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('推奨履歴の取得に失敗しました:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [page, rowsPerPage, sort, startDate, endDate, strategyFilter]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSortChange = (field: string) => {
    const [currentField, currentOrder] = sort.split('-');
    const newOrder = currentField === field ? (currentOrder === 'asc' ? 'desc' : 'asc') : 'desc';
    setSort(`${field}-${newOrder}`);
  };

  const handleRowClick = (sessionId: string) => {
    navigate(`/recommendations/${sessionId}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        推奨履歴
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <DatePicker
          label="開始日"
          value={startDate}
          onChange={(newValue) => setStartDate(newValue)}
          slotProps={{
            textField: {
              size: 'small'
            }
          }}
        />
        <DatePicker
          label="終了日"
          value={endDate}
          onChange={(newValue) => setEndDate(newValue)}
          slotProps={{
            textField: {
              size: 'small'
            }
          }}
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>戦略</InputLabel>
          <Select
            value={strategyFilter}
            label="戦略"
            onChange={(e) => setStrategyFilter(e.target.value)}
          >
            <MenuItem value="">すべて</MenuItem>
            <MenuItem value="成長株">成長株</MenuItem>
            <MenuItem value="配当株">配当株</MenuItem>
            <MenuItem value="バランス">バランス</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell 
                onClick={() => handleSortChange('date')}
                sx={{ cursor: 'pointer', fontWeight: 'bold' }}
              >
                日時 {sort.startsWith('date') && (sort.endsWith('asc') ? '↑' : '↓')}
              </TableCell>
              <TableCell 
                onClick={() => handleSortChange('principal')}
                sx={{ cursor: 'pointer', fontWeight: 'bold' }}
              >
                元本 {sort.startsWith('principal') && (sort.endsWith('asc') ? '↑' : '↓')}
              </TableCell>
              <TableCell>リスク許容度</TableCell>
              <TableCell>戦略</TableCell>
              <TableCell>プロンプト</TableCell>
              <TableCell>テクニカルフィルタ</TableCell>
              <TableCell>銘柄数</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">読み込み中...</TableCell>
              </TableRow>
            ) : sessions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">履歴がありません</TableCell>
              </TableRow>
            ) : (
              sessions.map((session) => (
                <StyledTableRow 
                  key={session.session_id} 
                  onClick={() => handleRowClick(session.session_id)}
                >
                  <TableCell>{dayjs(session.generated_at).format('YYYY/MM/DD HH:mm')}</TableCell>
                  <TableCell>¥{session.principal.toLocaleString()}</TableCell>
                  <TableCell>{session.risk_tolerance}</TableCell>
                  <TableCell>{session.strategy}</TableCell>
                  <TableCell>
                    <Tooltip title={session.prompt_name || 'デフォルト'} arrow>
                      <span>{session.prompt_name || 'デフォルト'}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={session.technical_filter || 'なし'} arrow>
                      <span>
                        {session.technical_filter 
                          ? `${session.technical_filter.substring(0, 15)}...` 
                          : 'なし'}
                      </span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{session.symbol_count}</TableCell>
                </StyledTableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={total}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="1ページあたりの行数:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} / ${count}`}
      />
    </Box>
  );
};

export default RecommendationHistory;
