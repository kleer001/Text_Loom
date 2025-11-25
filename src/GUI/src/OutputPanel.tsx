import React, { useState } from 'react';
import { Box, Paper, Typography, IconButton, Collapse, Alert, Chip } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CloseIcon from '@mui/icons-material/Close';
import type { ExecutionResponse } from './types';
import { OUTPUT_PANEL } from './constants';

interface OutputPanelProps {
  executionResult: ExecutionResponse | null;
  nodeName?: string;
  onClose: () => void;
}

const MessageList: React.FC<{ messages: string[]; severity: 'error' | 'warning' }> = ({ messages, severity }) => (
  <Box sx={{ px: 2, py: 1 }}>
    <Typography variant="subtitle2" color={`${severity}.main`} gutterBottom>
      {severity === 'error' ? 'Errors:' : 'Warnings:'}
    </Typography>
    {messages.map((message, idx) => (
      <Typography key={idx} variant="body2" color={`${severity}.main`} sx={{ fontFamily: 'monospace', mb: 0.5 }}>
        {message}
      </Typography>
    ))}
  </Box>
);

const OutputLine: React.FC<{ line: string; lineNumber: number }> = ({ line, lineNumber }) => (
  <Box sx={{ display: 'flex', gap: 1 }}>
    <Typography
      component="span"
      sx={{
        color: 'text.secondary',
        minWidth: OUTPUT_PANEL.LINE_NUMBER_WIDTH,
        textAlign: 'right',
        userSelect: 'none',
      }}
    >
      {lineNumber}
    </Typography>
    <Typography component="span" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
      {line}
    </Typography>
  </Box>
);

const OutputData: React.FC<{ data: string[][] }> = ({ data }) => (
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
      {data.map((outputArray, outputIdx) => (
        <Box key={outputIdx} sx={{ mb: outputIdx < data.length - 1 ? 2 : 0 }}>
          {outputArray.map((line, lineIdx) => (
            <OutputLine key={lineIdx} line={line} lineNumber={lineIdx + 1} />
          ))}
        </Box>
      ))}
    </Box>
  </Box>
);

const formatOutputForClipboard = (data: string[][]): string =>
  data.map(output => output.join('\n')).join('\n---\n');

const hasOutput = (executionResult: ExecutionResponse): boolean =>
  !!(executionResult.output_data && executionResult.output_data.length > 0);

const OutputPanelComponent: React.FC<OutputPanelProps> = ({ executionResult, nodeName, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleCopyOutput = () => {
    if (!executionResult?.output_data) return;
    navigator.clipboard.writeText(formatOutputForClipboard(executionResult.output_data));
  };

  if (!executionResult) return null;

  return (
    <Paper
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        maxHeight: isExpanded ? OUTPUT_PANEL.MAX_HEIGHT : OUTPUT_PANEL.HEADER_HEIGHT,
        minHeight: OUTPUT_PANEL.HEADER_HEIGHT,
        display: 'flex',
        flexDirection: 'column',
        transition: `max-height ${OUTPUT_PANEL.ANIMATION_DURATION} ease-in-out`,
      }}
      square
      elevation={3}
    >
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

      <Collapse in={isExpanded}>
        <Box sx={{ overflow: 'auto', maxHeight: `calc(${OUTPUT_PANEL.MAX_HEIGHT} - ${OUTPUT_PANEL.HEADER_HEIGHT})` }}>
          {executionResult.message && (
            <Alert
              severity={executionResult.success ? 'success' : 'error'}
              sx={{ m: 2, mb: 1 }}
            >
              {executionResult.message}
            </Alert>
          )}

          {executionResult.errors.length > 0 && <MessageList messages={executionResult.errors} severity="error" />}
          {executionResult.warnings.length > 0 && <MessageList messages={executionResult.warnings} severity="warning" />}

          {hasOutput(executionResult) ? (
            <OutputData data={executionResult.output_data!} />
          ) : (
            executionResult.errors.length === 0 && (
              <Box sx={{ px: 2, py: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  No output data
                </Typography>
              </Box>
            )
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export const OutputPanel = React.memo(OutputPanelComponent);
