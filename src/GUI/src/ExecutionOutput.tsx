// Execution Output Display - Shows node execution results

import React from 'react';
import { Box, Typography, Alert, Paper, IconButton } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import type { ExecutionResponse } from './types';

interface ExecutionOutputProps {
  executionResult: ExecutionResponse;
  onCopyOutput: () => void;
}

export const ExecutionOutput: React.FC<ExecutionOutputProps> = ({ executionResult, onCopyOutput }) => {
  return (
    <Box sx={{ mb: 2 }}>
      {/* Status Alert */}
      <Alert severity={executionResult.success ? 'success' : 'error'} sx={{ mb: 1 }}>
        {executionResult.message}
        <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
          Execution time: {executionResult.execution_time.toFixed(2)}ms
        </Typography>
      </Alert>

      {/* Output Data */}
      {executionResult.output_data && executionResult.output_data.length > 0 && (
        <Paper variant="outlined" sx={{ p: 1, mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle2">Output</Typography>
            <IconButton size="small" onClick={onCopyOutput} title="Copy to clipboard">
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Box>
          <Box
            sx={{
              fontFamily: 'monospace',
              fontSize: '12px',
              bgcolor: 'grey.50',
              p: 1,
              borderRadius: 1,
              maxHeight: '300px',
              overflow: 'auto',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {executionResult.output_data.map((output, idx) => (
              <Box key={idx} sx={{ mb: idx < executionResult.output_data!.length - 1 ? 2 : 0 }}>
                {output.map((line, lineIdx) => (
                  <Box key={lineIdx} sx={{ display: 'flex', gap: 1 }}>
                    <Typography
                      component="span"
                      sx={{
                        color: 'text.secondary',
                        minWidth: '30px',
                        textAlign: 'right',
                        userSelect: 'none',
                      }}
                    >
                      {lineIdx + 1}
                    </Typography>
                    <Typography component="span">{line}</Typography>
                  </Box>
                ))}
              </Box>
            ))}
          </Box>
        </Paper>
      )}

      {/* Execution Errors */}
      {executionResult.errors.length > 0 && (
        <Alert severity="error" sx={{ mb: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Execution Errors
          </Typography>
          {executionResult.errors.map((error, idx) => (
            <Typography key={idx} variant="body2" sx={{ fontFamily: 'monospace', fontSize: '12px' }}>
              • {error}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Execution Warnings */}
      {executionResult.warnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Warnings
          </Typography>
          {executionResult.warnings.map((warning, idx) => (
            <Typography key={idx} variant="body2" sx={{ fontFamily: 'monospace', fontSize: '12px' }}>
              • {warning}
            </Typography>
          ))}
        </Alert>
      )}
    </Box>
  );
};
