// Global Editor - Add/Edit global variables with validation
// Follows SRP: Only responsible for global variable input
// Follows DRY: Relies on backend validation instead of duplicating logic

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Box, TextField, Button, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface GlobalEditorProps {
  onSave: (key: string, value: string) => Promise<void>;
}

export const GlobalEditor: React.FC<GlobalEditorProps> = ({ onSave }) => {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const isMountedRef = useRef(true);

  // Track component mount status to prevent setState on unmounted component
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const handleSave = useCallback(async () => {
    // Basic client-side checks for UX (backend will do real validation)
    if (!key.trim()) {
      setError('Key cannot be empty');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await onSave(key, value);
      // Clear form on success (only if still mounted)
      if (isMountedRef.current) {
        setKey('');
        setValue('');
      }
    } catch (err) {
      // Display backend validation error (only if still mounted)
      if (isMountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to save global variable');
      }
    } finally {
      if (isMountedRef.current) {
        setIsSaving(false);
      }
    }
  }, [key, value, onSave]);

  const handleKeyChange = useCallback((newKey: string) => {
    // Auto-uppercase for UX convenience (backend requires uppercase)
    const uppercased = newKey.toUpperCase();
    setKey(uppercased);

    // Clear error when user starts typing
    if (error) {
      setError(null);
    }
  }, [error]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && key && value) {
      handleSave();
    }
  }, [key, value, handleSave]);

  return (
    <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <TextField
          size="small"
          label="Key"
          value={key}
          onChange={(e) => handleKeyChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="MY_GLOBAL"
          error={!!error}
          disabled={isSaving}
          sx={{ flex: 1 }}
        />
        <TextField
          size="small"
          label="Value"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Value"
          disabled={isSaving}
          sx={{ flex: 2 }}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleSave}
          disabled={!key || !value || isSaving}
        >
          {isSaving ? 'Adding...' : 'Add'}
        </Button>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};
