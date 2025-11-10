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

const AppContent: React.FC = () => {
  const { loadWorkspace, loading, error, nodes } = useWorkspace();
  const [selectedNodes, setSelectedNodes] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'details' | 'globals'>('details');

  // Load workspace on mount
  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  // Get the selected node's full data from workspace
  const selectedNode = selectedNodes.length === 1
    ? nodes.find(n => n.session_id === selectedNodes[0].id) || null
    : null;

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
            <>
              <GraphCanvas onSelectionChange={setSelectedNodes} />
              <AddNodeMenu variant="fab" />
            </>
          )}
        </Box>

        {/* Right Sidebar - Tabbed Interface */}
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
          {/* Tab Headers */}
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

          {/* Tab Content */}
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            {activeTab === 'details' && <NodeDetailsPanel node={selectedNode} />}
            {activeTab === 'globals' && <GlobalsPanel />}
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
