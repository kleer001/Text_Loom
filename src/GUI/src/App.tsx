// Main App Component - Application shell with layout

import React, { useEffect, useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';
import PublicIcon from '@mui/icons-material/Public';
import { WorkspaceProvider, useWorkspace } from './WorkspaceContext';
import { GraphCanvas } from './GraphCanvas';
import { NodeDetailsPanel } from './NodeDetailsPanel';
import { GlobalsPanel } from './GlobalsPanel';
import { AddNodeMenu } from './AddNodeMenu';
import { OutputPanel } from './OutputPanel';
import type { NodeResponse } from './types';

const AppContent: React.FC = () => {
  const { loadWorkspace, loading, error, lastExecutionResult, lastExecutedNodeName, clearExecutionResult } = useWorkspace();
  const [focusedNode, setFocusedNode] = useState<NodeResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'globals'>('details');

  // Load workspace on mount
  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

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

      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
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
              <>
                <GraphCanvas onNodeFocus={setFocusedNode} />
                <AddNodeMenu variant="fab" />
              </>
            )}
          </Box>

          <Paper
            sx={{
              width: 360,
              borderLeft: 1,
              borderColor: 'divider',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
            }}
            square
            elevation={0}
          >
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab
                value="details"
                label="Node Details"
                icon={<InfoIcon />}
                iconPosition="start"
              />
              <Tab
                value="globals"
                label="Globals"
                icon={<PublicIcon />}
                iconPosition="start"
              />
            </Tabs>

            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              {activeTab === 'details' && <NodeDetailsPanel node={focusedNode} />}
              {activeTab === 'globals' && <GlobalsPanel />}
            </Box>
          </Paper>
        </Box>

        <OutputPanel
          executionResult={lastExecutionResult}
          nodeName={lastExecutedNodeName || undefined}
          onClose={clearExecutionResult}
        />
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
