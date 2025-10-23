import React from 'react';
import { Box, Typography, TextField, Switch, Button, FormControlLabel, Paper } from '@mui/material';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useSelection } from '../../contexts/SelectionContext';
import type { Parameter } from '../../types/workspace';

const ParameterPanel: React.FC = () => {
  const { state, updateNodeParameter } = useWorkspace();
  const { selectedNodePaths } = useSelection();

  if (selectedNodePaths.length === 0) {
    return (
      <Box p={2}>
        <Typography variant="body2" color="textSecondary">
          Select a node to edit parameters
        </Typography>
      </Box>
    );
  }

  if (selectedNodePaths.length > 1) {
    return (
      <Box p={2}>
        <Typography variant="body2" color="textSecondary">
          Multiple nodes selected
        </Typography>
      </Box>
    );
  }

  const selectedNode = state.nodes.find(n => n.path === selectedNodePaths[0]);
  if (!selectedNode) return null;

  const handleChange = (paramName: string, value: any) => {
    updateNodeParameter(selectedNode.path, paramName, value);
  };

  return (
    <Paper sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {selectedNode.name}
      </Typography>
      <Typography variant="caption" color="textSecondary" display="block" mb={2}>
        {selectedNode.type.replace(/_/g, ' ')}
      </Typography>

      {Object.entries(selectedNode.parameters).map(([key, param]: [string, Parameter]) => (
        <Box key={key} mb={2}>
          {param.type === 'STRING' && (
            <TextField
              fullWidth
              label={key}
              value={param.value}
              placeholder={param.default}
              onChange={(e) => handleChange(key, e.target.value)}
              disabled={param.read_only}
              size="small"
            />
          )}
          
          {param.type === 'INT' && (
            <TextField
              fullWidth
              type="number"
              label={key}
              value={param.value}
              placeholder={param.default}
              onChange={(e) => handleChange(key, parseInt(e.target.value))}
              disabled={param.read_only}
              size="small"
            />
          )}

          {param.type === 'FLOAT' && (
            <TextField
              fullWidth
              type="number"
              label={key}
              value={param.value}
              placeholder={param.default}
              onChange={(e) => handleChange(key, parseFloat(e.target.value))}
              disabled={param.read_only}
              size="small"
              inputProps={{ step: 'any' }}
            />
          )}

          {param.type === 'TOGGLE' && (
            <FormControlLabel
              control={
                <Switch
                  checked={param.value}
                  onChange={(e) => handleChange(key, e.target.checked)}
                  disabled={param.read_only}
                />
              }
              label={key}
            />
          )}

          {param.type === 'BUTTON' && (
            <Button
              fullWidth
              variant="outlined"
              onClick={() => handleChange(key, true)}
              disabled={param.read_only}
            >
              {key}
            </Button>
          )}

          {param.type === 'STRINGLIST' && (
            <TextField
              fullWidth
              multiline
              rows={4}
              label={key}
              value={Array.isArray(param.value) ? param.value.join('\n') : param.value}
              placeholder={param.default}
              onChange={(e) => handleChange(key, e.target.value.split('\n'))}
              disabled={param.read_only}
              size="small"
            />
          )}
        </Box>
      ))}
    </Paper>
  );
};

export default ParameterPanel;