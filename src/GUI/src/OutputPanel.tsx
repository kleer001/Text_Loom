// Output Panel - Displays node execution output at bottom of window

import React, { useState } from 'react';
import { Box, Paper, Typography, IconButton, Collapse, Alert, Chip } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CloseIcon from '@mui/icons-material/Close';
import type { ExecutionResponse } from './types';

interface OutputPanelProps {
  executionResult: ExecutionResponse | null;
  nodeName?: string;
  onClose: () => void;
}

export const OutputPanel: React.FC<OutputPanelProps> = ({ executionResult, nodeName, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleCopyOutput = () => {
    if (!executionResult?.output_data) return;

    const text = executionResult.output_data
      .map(output => output.join('\n'))
      .join('\n---\n');

    navigator.clipboard.writeText(text);
  };

  if (!executionResult) return null;

  return (
    <Paper
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        maxHeight: isExpanded ? '40vh' : '48px',
        minHeight: '48px',
        display: 'flex',
        flexDirection: 'column',
        transition: 'max-height 0.2s ease-in-out',
      }}
      square
      elevation={3}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 2,
          py: 1,
          borderBottom: isExpanded ? 1 : 0,
          borderColor: 'divider',
          backgroundColor: 'background.default',
          cursor: 'pointer',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Typography variant="subtitle2" sx={{ flex: 1 }}>
          Output {nodeName && `- ${nodeName}`}
        </Typography>

        <Chip
          label={executionResult.node_state}
          size="small"
          color={executionResult.success ? 'success' : 'error'}
          sx={{ mr: 1 }}
        />

        <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
          {executionResult.execution_time.toFixed(2)}ms
        </Typography>

        <IconButton
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            handleCopyOutput();
          }}
          title="Copy output"
          disabled={!executionResult.output_data}
        >
          <ContentCopyIcon fontSize="small" />
        </IconButton>

        <IconButton
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
          title="Close output panel"
        >
          <CloseIcon fontSize="small" />
        </IconButton>

        <IconButton size="small" title={isExpanded ? 'Collapse' : 'Expand'}>
          {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {/* Content */}
      <Collapse in={isExpanded}>
        <Box sx={{ overflow: 'auto', maxHeight: 'calc(40vh - 48px)' }}>
          {/* Status Message */}
          {executionResult.message && (
            <Alert
              severity={executionResult.success ? 'success' : 'error'}
              sx={{ m: 2, mb: 1 }}
            >
              {executionResult.message}
            </Alert>
          )}

          {/* Errors */}
          {executionResult.errors.length > 0 && (
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2" color="error" gutterBottom>
                Errors:
              </Typography>
              {executionResult.errors.map((error, idx) => (
                <Typography key={idx} variant="body2" color="error" sx={{ fontFamily: 'monospace', mb: 0.5 }}>
                  {error}
                </Typography>
              ))}
            </Box>
          )}

          {/* Warnings */}
          {executionResult.warnings.length > 0 && (
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2" color="warning.main" gutterBottom>
                Warnings:
              </Typography>
              {executionResult.warnings.map((warning, idx) => (
                <Typography key={idx} variant="body2" color="warning.main" sx={{ fontFamily: 'monospace', mb: 0.5 }}>
                  {warning}
                </Typography>
              ))}
            </Box>
          )}

          {/* Output Data */}
          {executionResult.output_data && executionResult.output_data.length > 0 && (
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Output:
              </Typography>
              <Box
                sx={{
                  backgroundColor: 'grey.100',
                  borderRadius: 1,
                  p: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  overflow: 'auto',
                }}
              >
                {executionResult.output_data.map((outputArray, outputIdx) => (
                  <Box key={outputIdx} sx={{ mb: outputIdx < executionResult.output_data!.length - 1 ? 2 : 0 }}>
                    {outputArray.map((line, lineIdx) => (
                      <Box key={lineIdx} sx={{ display: 'flex', gap: 1 }}>
                        <Typography
                          component="span"
                          sx={{
                            color: 'text.secondary',
                            minWidth: '3ch',
                            textAlign: 'right',
                            userSelect: 'none',
                          }}
                        >
                          {lineIdx + 1}
                        </Typography>
                        <Typography component="span" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                          {line}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          {/* No Output Message */}
          {(!executionResult.output_data || executionResult.output_data.length === 0) &&
            executionResult.errors.length === 0 && (
              <Box sx={{ px: 2, py: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  No output data
                </Typography>
              </Box>
            )}
        </Box>
      </Collapse>
    </Paper>
  );
};
