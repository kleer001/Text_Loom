import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { apiClient } from './apiClient';
import type { TokenTotalsResponse, TokenHistoryEntry } from './types';

export const TokensPanel: React.FC = () => {
  const [totals, setTotals] = useState<TokenTotalsResponse>({
    input_tokens: 0,
    output_tokens: 0,
    total_tokens: 0
  });
  const [history, setHistory] = useState<TokenHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const loadTokenData = async (): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const [totalsData, historyData] = await Promise.all([
        apiClient.getTokenTotals(),
        apiClient.getTokenHistory(),
      ]);

      setTotals(totalsData);
      setHistory(historyData.history);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load token data';
      setError(message);
      console.error('Token data load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async (): Promise<void> => {
    if (!window.confirm('Are you sure you want to reset all token tracking data? This cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await apiClient.resetTokenTracking();
      setSuccessMessage(result.message);
      setTotals({ input_tokens: 0, output_tokens: 0, total_tokens: 0 });
      setHistory([]);

      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to reset token data';
      setError(message);
      console.error('Token reset error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  useEffect(() => {
    loadTokenData();
  }, []);

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2, overflow: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Token Tracking</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={loadTokenData}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            size="small"
            color="error"
            startIcon={<DeleteSweepIcon />}
            onClick={handleReset}
            disabled={loading || totals.total_tokens === 0}
          >
            Reset
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Input Tokens
              </Typography>
              <Typography variant="h5" component="div">
                {formatNumber(totals.input_tokens)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Output Tokens
              </Typography>
              <Typography variant="h5" component="div">
                {formatNumber(totals.output_tokens)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Total Tokens
              </Typography>
              <Typography variant="h5" component="div">
                {formatNumber(totals.total_tokens)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ mb: 2 }} />

      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Query History ({history.length})
      </Typography>

      {history.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No token usage data available. Execute a QueryNode to start tracking.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Node Name</TableCell>
                <TableCell align="right">Input</TableCell>
                <TableCell align="right">Output</TableCell>
                <TableCell align="right">Total</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((entry, index) => (
                <TableRow key={index} hover>
                  <TableCell>{formatTimestamp(entry.timestamp)}</TableCell>
                  <TableCell>{entry.node_name}</TableCell>
                  <TableCell align="right">{formatNumber(entry.input_tokens)}</TableCell>
                  <TableCell align="right">{formatNumber(entry.output_tokens)}</TableCell>
                  <TableCell align="right">
                    <strong>{formatNumber(entry.total_tokens)}</strong>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};
