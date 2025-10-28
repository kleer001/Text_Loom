// Main App Component - Application shell with layout

import React, { useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { WorkspaceProvider, useWorkspace } from './WorkspaceContext';
import { GraphCanvas } from './GraphCanvas';
import { NodeDetailsPanel } from './NodeDetailsPanel';

const AppContent: React.FC = () => {
  const { loadWorkspace, loading, error, getSelectedNode } = useWorkspace();

  // Load workspace on mount
  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  const selectedNode = getSelectedNode();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            TextLoom Workspace
          </Typography>
          <Button
            color="inherit"
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
            onClick={loadWorkspace}
            disabled={loading}
          >
            Refresh
          </Button>
        </Toolbar>
      </AppBar>

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          onClose={() => loadWorkspace()}
          sx={{ m: 2 }}
        >
          {error} - Click to retry
        </Alert>
      )}

      {/* Main Content Area */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Graph Canvas */}
        <Box sx={{ flex: 1, position: 'relative' }}>
          {loading && !error ? (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
              }}
            >
              <CircularProgress />
            </Box>
          ) : (
            <GraphCanvas />
          )}
        </Box>

        {/* Right Sidebar - Node Details */}
        <Paper
          sx={{
            width: 320,
            borderLeft: 1,
            borderColor: 'divider',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
          square
          elevation={0}
        >
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">Node Details</Typography>
          </Box>
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            <NodeDetailsPanel node={selectedNode} />
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export const App: React.FC = () => {
  return (
    <WorkspaceProvider>
      <AppContent />
    </WorkspaceProvider>
  );
};
