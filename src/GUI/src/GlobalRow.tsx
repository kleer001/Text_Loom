// Global Row - Display and edit a single global variable
// Follows SRP: Only responsible for displaying one global variable

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Box, Typography, TextField, IconButton, Chip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';

interface GlobalRowProps {
  globalKey: string;
  value: string | number | boolean;
  onEdit: (key: string, newValue: string) => Promise<void>;
  onDelete: (key: string) => Promise<void>;
}

export const GlobalRow: React.FC<GlobalRowProps> = ({ globalKey, value, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(String(value));
  const [isDeleting, setIsDeleting] = useState(false);
  const isMountedRef = useRef(true);

  // Track component mount status to prevent setState on unmounted component
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const handleStartEdit = useCallback(() => {
    setEditValue(String(value));
    setIsEditing(true);
  }, [value]);

  const handleCancelEdit = useCallback(() => {
    setEditValue(String(value));
    setIsEditing(false);
  }, [value]);

  const handleSaveEdit = useCallback(async () => {
    if (editValue === String(value)) {
      setIsEditing(false);
      return;
    }

    try {
      await onEdit(globalKey, editValue);
      if (isMountedRef.current) {
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Failed to edit global:', error);
      // Keep editing mode open on error
    }
  }, [globalKey, editValue, value, onEdit]);

  const handleDelete = useCallback(async () => {
    if (!confirm(`Delete global variable "${globalKey}"?`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await onDelete(globalKey);
      // Note: Component will likely unmount after successful delete, so no setState needed
    } catch (error) {
      console.error('Failed to delete global:', error);
      if (isMountedRef.current) {
        setIsDeleting(false);
      }
    }
  }, [globalKey, onDelete]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  }, [handleSaveEdit, handleCancelEdit]);

  // Infer type from value
  const valueType = typeof value;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: 1.5,
        borderBottom: 1,
        borderColor: 'divider',
        '&:hover': {
          bgcolor: 'action.hover',
        },
        opacity: isDeleting ? 0.5 : 1,
      }}
    >
      {/* Key */}
      <Typography
        variant="body2"
        fontWeight="bold"
        sx={{
          fontFamily: 'monospace',
          minWidth: '150px',
          color: 'primary.main',
        }}
      >
        {globalKey}
      </Typography>

      {/* Type Chip */}
      <Chip label={valueType} size="small" variant="outlined" sx={{ minWidth: '70px' }} />

      {/* Value */}
      {isEditing ? (
        <TextField
          size="small"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onKeyDown={handleKeyPress}
          autoFocus
          fullWidth
          sx={{ fontFamily: 'monospace' }}
          InputProps={{
            endAdornment: (
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <IconButton size="small" onClick={handleSaveEdit} color="primary">
                  <CheckIcon fontSize="small" />
                </IconButton>
                <IconButton size="small" onClick={handleCancelEdit}>
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            ),
          }}
        />
      ) : (
        <>
          <Typography
            variant="body2"
            sx={{
              flex: 1,
              fontFamily: 'monospace',
              fontSize: '13px',
              bgcolor: 'grey.50',
              p: 1,
              borderRadius: 1,
            }}
          >
            {String(value)}
          </Typography>

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <IconButton size="small" onClick={handleStartEdit} disabled={isDeleting} title="Edit value">
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              onClick={handleDelete}
              disabled={isDeleting}
              color="error"
              title="Delete global"
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        </>
      )}
    </Box>
  );
};
