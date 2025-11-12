// Parameter Editor Component - Type-specific parameter editing widgets

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Typography,
} from '@mui/material';
import type { ParameterInfo } from './types';

interface ParameterEditorProps {
  name: string;
  parameter: ParameterInfo;
  onChange: (name: string, value: string | number | boolean | string[]) => void;
  debounceMs?: number;
}

export const ParameterEditor: React.FC<ParameterEditorProps> = ({
  name,
  parameter,
  onChange,
  debounceMs = 500,
}) => {
  const [localValue, setLocalValue] = useState<string | number | boolean | string[]>(parameter.value);
  const [error, setError] = useState<string>('');
  const [hasGlobalRef, setHasGlobalRef] = useState<boolean>(false);

  // Update local value when parameter changes externally
  useEffect(() => {
    setLocalValue(parameter.value);

    // Detect global variable references ($VAR)
    if (typeof parameter.value === 'string') {
      setHasGlobalRef(/\$[A-Z_][A-Z0-9_]*/.test(parameter.value));
    } else {
      setHasGlobalRef(false);
    }
  }, [parameter.value]);

  // Debounced onChange for text inputs
  useEffect(() => {
    if (parameter.type === 'STRING' || parameter.type === 'INT' || parameter.type === 'FLOAT') {
      const timer = setTimeout(() => {
        // Only call onChange if value actually changed
        if (localValue !== parameter.value && !error) {
          onChange(name, localValue);
        }
      }, debounceMs);

      return () => clearTimeout(timer);
    }
  }, [localValue, parameter.value, parameter.type, name, onChange, debounceMs, error]);

  // Validation helper
  const validateValue = useCallback((value: string | number | boolean | string[], type: string): string => {
    if (type === 'INT') {
      const num = Number(value);
      if (isNaN(num)) return 'Must be a valid number';
      if (!Number.isInteger(num)) return 'Must be an integer';
    } else if (type === 'FLOAT') {
      const num = Number(value);
      if (isNaN(num)) return 'Must be a valid number';
    }
    return '';
  }, []);

  const handleChange = (newValue: string | number | boolean | string[]) => {
    setLocalValue(newValue);

    // Validate immediately for better UX
    const validationError = validateValue(newValue, parameter.type);
    setError(validationError);
  };

  // Render different widgets based on parameter type
  const renderWidget = () => {
    const isReadOnly = parameter.read_only;

    switch (parameter.type) {
      case 'STRING':
        return (
          <TextField
            fullWidth
            size="small"
            value={localValue}
            onChange={(e) => handleChange(e.target.value)}
            disabled={isReadOnly}
            placeholder={String(parameter.default)}
            error={!!error}
            helperText={error || (hasGlobalRef ? 'Contains global variable reference' : '')}
            sx={{
              '& .MuiInputBase-input': {
                fontFamily: hasGlobalRef ? 'monospace' : 'inherit',
              },
            }}
          />
        );

      case 'INT':
      case 'FLOAT':
        return (
          <TextField
            fullWidth
            size="small"
            type="number"
            value={localValue}
            onChange={(e) => handleChange(e.target.value)}
            disabled={isReadOnly}
            placeholder={String(parameter.default)}
            error={!!error}
            helperText={error}
            inputProps={{
              step: parameter.type === 'INT' ? 1 : 0.01,
            }}
          />
        );

      case 'TOGGLE':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={Boolean(localValue)}
                onChange={(e) => {
                  const newValue = e.target.checked;
                  setLocalValue(newValue);
                  onChange(name, newValue); // No debounce for toggle
                }}
                disabled={isReadOnly}
              />
            }
            label={localValue ? 'On' : 'Off'}
          />
        );

      case 'BUTTON':
        return (
          <Button
            variant="outlined"
            size="small"
            fullWidth
            disabled={isReadOnly}
            onClick={() => onChange(name, true)}
          >
            {name}
          </Button>
        );

      case 'STRINGLIST':
        return (
          <TextField
            fullWidth
            size="small"
            multiline
            rows={3}
            value={Array.isArray(localValue) ? localValue.join('\n') : localValue}
            onChange={(e) => {
              const lines = e.target.value.split('\n');
              handleChange(lines);
            }}
            disabled={isReadOnly}
            placeholder={Array.isArray(parameter.default) ? parameter.default.join('\n') : String(parameter.default)}
            error={!!error}
            helperText={error || 'One item per line'}
          />
        );

      case 'MENU':
        // TODO: Need to get menu options from backend metadata
        // For now, treat as string
        return (
          <TextField
            fullWidth
            size="small"
            value={localValue}
            onChange={(e) => handleChange(e.target.value)}
            disabled={isReadOnly}
            placeholder={String(parameter.default)}
            error={!!error}
            helperText={error || 'Menu type (options needed from backend)'}
          />
        );

      default:
        // Fallback for unknown types
        return (
          <TextField
            fullWidth
            size="small"
            value={String(localValue)}
            onChange={(e) => handleChange(e.target.value)}
            disabled={isReadOnly}
            placeholder={String(parameter.default)}
            error={!!error}
            helperText={error}
          />
        );
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, minWidth: '150px' }}>
        <Typography variant="body2" fontWeight="bold">
          {name}
        </Typography>
        {parameter.read_only && (
          <Typography variant="caption" color="text.secondary">
            (read-only)
          </Typography>
        )}
      </Box>
      <Box sx={{ flex: 1 }}>
        {renderWidget()}
      </Box>
    </Box>
  );
};
