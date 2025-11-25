// Globals Panel - Manage global variables
// Follows SOLID: Coordinates GlobalEditor and GlobalRow components

import React, { useCallback } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useWorkspace } from './WorkspaceContext';
import { GlobalEditor } from './GlobalEditor';
import { GlobalRow } from './GlobalRow';

const GlobalsPanelComponent: React.FC = () => {
  const { globals, setGlobal, deleteGlobal } = useWorkspace();

  const handleSave = useCallback(async (key: string, value: string) => {
    // Parse value to infer type
    let parsedValue: string | number | boolean = value;

    // Try to parse as number
    if (!isNaN(Number(value)) && value.trim() !== '') {
      parsedValue = Number(value);
    }
    // Try to parse as boolean
    else if (value.toLowerCase() === 'true') {
      parsedValue = true;
    } else if (value.toLowerCase() === 'false') {
      parsedValue = false;
    }

    await setGlobal(key, parsedValue);
  }, [setGlobal]);

  const handleEdit = useCallback(async (key: string, newValue: string) => {
    // Parse value to infer type
    let parsedValue: string | number | boolean = newValue;

    // Try to parse as number
    if (!isNaN(Number(newValue)) && newValue.trim() !== '') {
      parsedValue = Number(newValue);
    }
    // Try to parse as boolean
    else if (newValue.toLowerCase() === 'true') {
      parsedValue = true;
    } else if (newValue.toLowerCase() === 'false') {
      parsedValue = false;
    }

    await setGlobal(key, parsedValue);
  }, [setGlobal]);

  const handleDelete = useCallback(async (key: string) => {
    await deleteGlobal(key);
  }, [deleteGlobal]);

  const globalEntries = Object.entries(globals).sort(([a], [b]) => a.localeCompare(b));

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Global Variables</Typography>
        <Typography variant="caption" color="text.secondary">
          Manage global variables accessible via $VARNAME in parameters
        </Typography>
      </Box>

      {/* Add New Global */}
      <GlobalEditor onSave={handleSave} />

      {/* Globals List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {globalEntries.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
            <Typography variant="body2">No global variables defined</Typography>
            <Typography variant="caption">
              Add a global variable above to get started
            </Typography>
          </Box>
        ) : (
          <Paper variant="outlined" sx={{ m: 2 }}>
            {globalEntries.map(([key, value]) => (
              <GlobalRow
                key={key}
                globalKey={key}
                value={value}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </Paper>
        )}
      </Box>

      {/* Footer Info */}
      {globalEntries.length > 0 && (
        <Box sx={{ p: 1.5, borderTop: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
          <Typography variant="caption" color="text.secondary">
            {globalEntries.length} global variable{globalEntries.length !== 1 ? 's' : ''} defined
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export const GlobalsPanel = React.memo(GlobalsPanelComponent);
