// Node Details Panel - Shows information about selected node

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, Typography, Divider, Chip, TextField, IconButton, Button, CircularProgress } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import type { NodeResponse } from './types';
import { useWorkspace } from './WorkspaceContext';
import { ParameterEditor } from './ParameterEditor';

interface NodeDetailsPanelProps {
  node: NodeResponse | null;
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node }) => {
  // All hooks must be called unconditionally at the top level (Rules of Hooks)
  const { updateNode, executeNode } = useWorkspace();
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [nameError, setNameError] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const isMountedRef = useRef(true);

  // Track component mount status to prevent setState on unmounted component
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Reset editing state when node changes
  useEffect(() => {
    setIsEditing(false);
    setEditName('');
    setNameError('');
  }, [node?.session_id]);

  // Wrap handleCook in useCallback to prevent unnecessary re-renders
  const handleCook = useCallback(async () => {
    if (isExecuting || !node) return;

    setIsExecuting(true);
    try {
      // Execute node - result will be shown in the bottom output panel
      await executeNode(node.session_id);
    } catch (error) {
      console.error('Failed to execute node:', error);
    } finally {
      if (isMountedRef.current) {
        setIsExecuting(false);
      }
    }
  }, [node, isExecuting, executeNode]);

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
    if (!node) return;
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
    if (!node) return;

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

      // Success - exit edit mode (only if still mounted)
      if (isMountedRef.current) {
        setIsEditing(false);
        setEditName('');
        setNameError('');
      }
    } catch (error) {
      // Show error message (only if still mounted)
      if (isMountedRef.current) {
        setNameError(error instanceof Error ? error.message : 'Failed to rename node');
      }
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
    if (!node) return;
    try {
      await updateNode(node.session_id, {
        parameters: {
          [paramName]: value,
        },
      });
    } catch (error) {
      console.error('Failed to update parameter:', paramName, error);
    }
  }, [node, updateNode]);

  // Conditional rendering AFTER all hooks are called
  if (!node) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary' }}>
        <Typography variant="body2">
          Select a node to view details
        </Typography>
      </Box>
    );
  }

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
