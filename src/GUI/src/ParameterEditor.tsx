// Parameter Editor Component - Type-specific parameter editing widgets

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  IconButton,
  Tooltip,
} from '@mui/material';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import type { ParameterInfo } from './types';

interface ParameterEditorProps {
  name: string;
  parameter: ParameterInfo;
  onChange: (name: string, value: string | number | boolean | string[]) => void;
  debounceMs?: number;
}

// Helper function to detect if a parameter represents a file/folder path
const isPathParameter = (paramName: string): 'file' | 'folder' | null => {
  const lowerName = paramName.toLowerCase();

  // Exclude json_path (it's a JSONPath query, not a filesystem path)
  if (lowerName === 'json_path') {
    return null;
  }

  // Check for folder-related parameters
  if (lowerName.includes('folder') || lowerName === 'folder_path') {
    return 'folder';
  }

  // Check for file-related parameters
  if (lowerName.includes('file') || lowerName.includes('path')) {
    return 'file';
  }

  return null;
};

export const ParameterEditor: React.FC<ParameterEditorProps> = ({
  name,
  parameter,
  onChange,
  debounceMs = 500,
}) => {
  const [localValue, setLocalValue] = useState<string | number | boolean | string[]>(parameter.value);
  const [error, setError] = useState<string>('');
  const [hasGlobalRef, setHasGlobalRef] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // Helper to parse menu options from value
  const parseMenuOptions = useCallback((value: string | number | boolean | string[]): Record<string, string> | null => {
    if (typeof value !== 'string') return null;

    try {
      // The backend stores menu options as a Python dict string like "{'key': 'Label', ...}"
      // We need to convert Python dict syntax to JSON
      const jsonStr = value
        .replace(/'/g, '"')  // Replace single quotes with double quotes
        .replace(/True/g, 'true')
        .replace(/False/g, 'false')
        .replace(/None/g, 'null');

      const parsed = JSON.parse(jsonStr);
      if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
        return parsed as Record<string, string>;
      }
    } catch (e) {
      // Not a dict, might be a selected value or invalid format
      return null;
    }
    return null;
  }, []);

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

  // Handle file browser button click
  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Handle file selection from browser
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Get the path - in web browsers, we get the file name
      // For Electron apps, we could get the full path
      const file = files[0];

      // @ts-ignore - webkitRelativePath is available when directory selection is used
      const path = file.webkitRelativePath || file.name;

      handleChange(path);

      // Reset the input so the same file can be selected again
      event.target.value = '';
    }
  };

  // Render different widgets based on parameter type
  const renderWidget = () => {
    const isReadOnly = parameter.read_only;

    switch (parameter.type) {
      case 'STRING': {
        const pathType = isPathParameter(name);
        const showBrowser = pathType !== null && !isReadOnly;

        return (
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
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
            {showBrowser && (
              <>
                <input
                  ref={fileInputRef}
                  type="file"
                  style={{ display: 'none' }}
                  onChange={handleFileSelect}
                  {...(pathType === 'folder' ? { webkitdirectory: '', directory: '' } : {})}
                />
                <Tooltip title={pathType === 'folder' ? 'Browse for folder' : 'Browse for file'}>
                  <IconButton
                    size="small"
                    onClick={handleBrowseClick}
                    sx={{ mt: 0.5 }}
                  >
                    {pathType === 'folder' ? <FolderOpenIcon /> : <InsertDriveFileIcon />}
                  </IconButton>
                </Tooltip>
              </>
            )}
          </Box>
        );
      }

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

      case 'MENU': {
        // Parse menu options from the value (which contains a Python dict string)
        const menuOptions = parseMenuOptions(parameter.value);

        if (!menuOptions || Object.keys(menuOptions).length === 0) {
          // Fallback to text field if we can't parse options
          return (
            <TextField
              fullWidth
              size="small"
              value={localValue}
              onChange={(e) => handleChange(e.target.value)}
              disabled={isReadOnly}
              placeholder={String(parameter.default)}
              error={!!error}
              helperText={error || 'No menu options available'}
            />
          );
        }

        // Determine selected value: if localValue is a dict string, select first option
        // If it's a plain key, use that
        const selectedValue = parseMenuOptions(localValue) ? Object.keys(menuOptions)[0] : String(localValue);

        return (
          <FormControl fullWidth size="small">
            <Select
              value={selectedValue}
              onChange={(e) => {
                const newValue = e.target.value;
                setLocalValue(newValue);
                onChange(name, newValue); // No debounce for menu selection
              }}
              disabled={isReadOnly}
            >
              {Object.entries(menuOptions).map(([key, label]) => (
                <MenuItem key={key} value={key}>
                  {label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      }

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
