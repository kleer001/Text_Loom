// Node Details Panel - Shows information about selected node

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, Typography, Divider, Chip, TextField, IconButton, Button, CircularProgress } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import type { NodeResponse, ExecutionResponse } from './types';
import { useWorkspace } from './WorkspaceContext';
import { ParameterEditor } from './ParameterEditor';
import { ExecutionOutput } from './ExecutionOutput';

interface NodeDetailsPanelProps {
  node: NodeResponse | null;
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node }) => {
  // Early return BEFORE any hooks to comply with Rules of Hooks
  if (!node) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary' }}>
        <Typography variant="body2">
          Select a node to view details
        </Typography>
      </Box>
    );
  }

  const { updateNode, executeNode } = useWorkspace();
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [nameError, setNameError] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Reset editing state when node changes
  useEffect(() => {
    setIsEditing(false);
    setEditName('');
    setNameError('');
    setExecutionResult(null);
  }, [node.session_id]);

  // Wrap handleCook in useCallback to prevent unnecessary re-renders
  const handleCook = useCallback(async () => {
    if (isExecuting) return;

    setIsExecuting(true);
    try {
      const result = await executeNode(node.session_id);
      setExecutionResult(result);
    } catch (error) {
      console.error('Failed to execute node:', error);
    } finally {
      setIsExecuting(false);
    }
  }, [node.session_id, isExecuting, executeNode]);

  // Keyboard shortcut for Cook (Shift+C)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === 'C' && !isExecuting) {
        e.preventDefault();
        handleCook();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isExecuting, handleCook]);

  const handleEditClick = () => {
    setEditName(node.name);
    setIsEditing(true);
    setNameError('');
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditName('');
    setNameError('');
  };

  const handleSaveEdit = async () => {
    const trimmedName = editName.trim();

    if (!trimmedName) {
      setNameError('Name cannot be empty');
      return;
    }

    if (trimmedName === node.name) {
      handleCancelEdit();
      return;
    }

    try {
      // Call the workspace context to update the node (updates both API and local state)
      await updateNode(node.session_id, { name: trimmedName });

      // Success - exit edit mode
      setIsEditing(false);
      setEditName('');
      setNameError('');
    } catch (error) {
      // Show error message
      setNameError(error instanceof Error ? error.message : 'Failed to rename node');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  const handleParameterChange = useCallback(async (paramName: string, value: string | number | boolean | string[]) => {
    try {
      await updateNode(node.session_id, {
        parameters: {
          [paramName]: value,
        },
      });
    } catch (error) {
      console.error('Failed to update parameter:', paramName, error);
    }
  }, [node.session_id, updateNode]);

  const handleCopyOutput = useCallback(() => {
    if (!executionResult?.output_data) return;

    const text = executionResult.output_data
      .map(output => output.join('\n'))
      .join('\n---\n');

    navigator.clipboard.writeText(text);
  }, [executionResult]);

  return (
    <Box sx={{ p: 2, overflow: 'auto', height: '100%' }}>
      {/* Header with editable name */}
      {isEditing ? (
        <Box sx={{ mb: 2 }}>
          <TextField
            inputRef={inputRef}
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onKeyDown={handleKeyDown}
            error={!!nameError}
            helperText={nameError}
            size="small"
            fullWidth
            placeholder="Node name"
            InputProps={{
              endAdornment: (
                <>
                  <IconButton size="small" onClick={handleSaveEdit} color="primary">
                    <CheckIcon fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={handleCancelEdit}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </>
              ),
            }}
          />
        </Box>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Typography variant="h6" sx={{ flex: 1 }}>
            {node.name}
          </Typography>
          <IconButton size="small" onClick={handleEditClick} title="Rename node (F2)">
            <EditIcon fontSize="small" />
          </IconButton>
        </Box>
      )}
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {node.type}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
        {node.path}
      </Typography>

      <Divider sx={{ my: 2 }} />

      {/* State */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          State
        </Typography>
        <Chip
          label={node.state}
          size="small"
          color={node.state === 'unchanged' ? 'success' : 'warning'}
        />
        <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
          Cook count: {node.cook_count}
        </Typography>
      </Box>

      {/* Cook Button */}
      <Button
        variant="contained"
        color="primary"
        fullWidth
        startIcon={isExecuting ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
        onClick={handleCook}
        disabled={isExecuting}
        sx={{ mb: 2 }}
      >
        {isExecuting ? 'Cooking...' : 'Cook Node (Shift+C)'}
      </Button>

      {/* Execution Results */}
      {executionResult && (
        <ExecutionOutput executionResult={executionResult} onCopyOutput={handleCopyOutput} />
      )}

      <Divider sx={{ my: 2 }} />

      {/* Parameters */}
      <Typography variant="subtitle2" gutterBottom>
        Parameters
      </Typography>
      {Object.keys(node.parameters).length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No parameters
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {Object.entries(node.parameters).map(([name, param]) => (
            <ParameterEditor
              key={name}
              name={name}
              parameter={param}
              onChange={handleParameterChange}
            />
          ))}
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Inputs */}
      <Typography variant="subtitle2" gutterBottom>
        Inputs
      </Typography>
      {node.inputs.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No inputs
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {node.inputs.map((input) => (
            <Box key={input.index} sx={{ mb: 1 }}>
              <Typography variant="body2">
                [{input.index}] {input.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {input.data_type} • {input.connected ? 'Connected' : 'Not connected'}
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Outputs */}
      <Typography variant="subtitle2" gutterBottom>
        Outputs
      </Typography>
      {node.outputs.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No outputs
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {node.outputs.map((output) => (
            <Box key={output.index} sx={{ mb: 1 }}>
              <Typography variant="body2">
                [{output.index}] {output.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {output.data_type} • {output.connection_count} connection(s)
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      {/* Errors */}
      {node.errors.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" color="error" gutterBottom>
            Errors
          </Typography>
          {node.errors.map((error, idx) => (
            <Typography key={idx} variant="body2" color="error" sx={{ mb: 0.5 }}>
              • {error}
            </Typography>
          ))}
        </>
      )}

      {/* Warnings */}
      {node.warnings.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" color="warning.main" gutterBottom>
            Warnings
          </Typography>
          {node.warnings.map((warning, idx) => (
            <Typography key={idx} variant="body2" color="warning.main" sx={{ mb: 0.5 }}>
              • {warning}
            </Typography>
          ))}
        </>
      )}
    </Box>
  );
};
