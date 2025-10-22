import React, { useState } from 'react';
import { Box, Typography, Button, Paper, List, ListItem, Alert, CircularProgress } from '@mui/material';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useSelection } from '../../contexts/SelectionContext';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const OutputPanel: React.FC = () => {
  const { state, executeNode } = useWorkspace();
  const { selectedNodePaths } = useSelection();
  const [executing, setExecuting] = useState(false);
  const [output, setOutput] = useState<string[] | null>(null);
  const [execTime, setExecTime] = useState<number | null>(null);

  if (selectedNodePaths.length === 0) {
    return (
      <Box p={2}>
        <Typography variant="body2" color="textSecondary">
          Select a node to view output
        </Typography>
      </Box>
    );
  }

  const selectedNode = state.nodes.find(n => n.path === selectedNodePaths[0]);
  if (!selectedNode) return null;

  const handleExecute = async () => {
    setExecuting(true);
    const result = await executeNode(selectedNode.path);
    setExecuting(false);
    
    if (result) {
      setOutput(result.output || []);
      setExecTime(result.execution_time);
    }
  };

  return (
    <Paper sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Output</Typography>
        <Button
          variant="contained"
          startIcon={executing ? <CircularProgress size={16} /> : <PlayArrowIcon />}
          onClick={handleExecute}
          disabled={executing}
          size="small"
        >
          Execute
        </Button>
      </Box>

      {selectedNode.errors.length > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {selectedNode.errors.map((err, idx) => (
            <div key={idx}>{err}</div>
          ))}
        </Alert>
      )}

      {selectedNode.warnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {selectedNode.warnings.map((warn, idx) => (
            <div key={idx}>{warn}</div>
          ))}
        </Alert>
      )}

      {execTime !== null && (
        <Typography variant="caption" color="textSecondary" display="block" mb={1}>
          Execution time: {execTime.toFixed(2)}ms
        </Typography>
      )}

      {output && (
        <List dense>
          {output.map((item, idx) => (
            <ListItem key={idx} sx={{ bgcolor: idx % 2 === 0 ? 'grey.100' : 'white' }}>
              <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                [{idx}] {item}
              </Typography>
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default OutputPanel;