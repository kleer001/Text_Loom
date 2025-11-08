// Global Editor - Add/Edit global variables with validation
// Follows SRP: Only responsible for global variable input and validation

import React, { useState, useCallback } from 'react';
import { Box, TextField, Button, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface GlobalEditorProps {
  onSave: (key: string, value: string) => Promise<void>;
}

// Validation function for global variable keys
const validateGlobalKey = (key: string): string | null => {
  if (!key) {
    return 'Key cannot be empty';
  }
  if (key.length < 2) {
    return 'Key must be at least 2 characters long';
  }
  if (key.startsWith('$')) {
    return 'Key cannot start with $ ($ is for references, not definitions)';
  }
  if (!/^[A-Z_][A-Z0-9_]*$/.test(key)) {
    return 'Key must be uppercase letters, numbers, and underscores only';
  }
  return null;
};

export const GlobalEditor: React.FC<GlobalEditorProps> = ({ onSave }) => {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = useCallback(async () => {
    // Validate key
    const validationError = validateGlobalKey(key);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await onSave(key, value);
      // Clear form on success
      setKey('');
      setValue('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save global variable');
    } finally {
      setIsSaving(false);
    }
  }, [key, value, onSave]);

  const handleKeyChange = useCallback((newKey: string) => {
    // Auto-uppercase for convenience
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
