// Main App Component - Application shell with layout

import React, { useEffect, useState, useCallback } from 'react';
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
import { FileMenu } from './FileMenu';
import { AutosaveRecoveryDialog } from './AutosaveRecoveryDialog';
import { useFileManager } from './hooks/useFileManager';
import { fileManager } from './services/fileManager';
import { apiClient } from './apiClient';
import type { NodeResponse } from './types';

const AppContent: React.FC = () => {
  const { loadWorkspace, loading, error, lastExecutionResult, lastExecutedNodeName, clearExecutionResult } = useWorkspace();
  const { save, saveAs, open, newWorkspace, isDirty, markClean } = useFileManager();
  const [focusedNode, setFocusedNode] = useState<NodeResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'globals'>('details');
  const [autosaveRecovery, setAutosaveRecovery] = useState<{
    show: boolean;
    timestamp: number;
    filePath: string | null;
    data: Record<string, any> | null;
  }>({
    show: false,
    timestamp: 0,
    filePath: null,
    data: null,
  });

  // Check for autosave on mount
  useEffect(() => {
    const checkAutosave = async () => {
      const autosave = await fileManager.getAutosave();
      if (autosave) {
        setAutosaveRecovery({
          show: true,
          timestamp: autosave.timestamp,
          filePath: autosave.currentFilePath,
          data: autosave.flowstateData,
        });
      } else {
        // No autosave, load workspace normally
        loadWorkspace();
      }
    };

    checkAutosave();
  }, [loadWorkspace]);

  // Handle autosave recovery
  const handleRecoverAutosave = useCallback(async () => {
    if (autosaveRecovery.data) {
      try {
        await apiClient.importWorkspace(autosaveRecovery.data);
        if (autosaveRecovery.filePath) {
          fileManager.setCurrentFilePath(autosaveRecovery.filePath);
        }
        await loadWorkspace();
        markClean();
      } catch (err) {
        console.error('Failed to recover autosave:', err);
      }
    }

    setAutosaveRecovery({ show: false, timestamp: 0, filePath: null, data: null });
  }, [autosaveRecovery, loadWorkspace, markClean]);

  const handleDiscardAutosave = useCallback(async () => {
    await fileManager.clearAutosave();
    setAutosaveRecovery({ show: false, timestamp: 0, filePath: null, data: null });
    loadWorkspace();
  }, [loadWorkspace]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if we're in an input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return;
      }

      // Ctrl+S - Save
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        save();
      }

      // Ctrl+Shift+S - Save-as
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        saveAs();
      }

      // Ctrl+O - Open
      if (e.ctrlKey && e.key === 'o') {
        e.preventDefault();
        open();
      }

      // Ctrl+N - New
      if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        newWorkspace();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [save, saveAs, open, newWorkspace]);

  // Warn on page unload if there are unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Autosave Recovery Dialog */}
      <AutosaveRecoveryDialog
        open={autosaveRecovery.show}
        timestamp={autosaveRecovery.timestamp}
        filePath={autosaveRecovery.filePath}
        onRecover={handleRecoverAutosave}
        onDiscard={handleDiscardAutosave}
      />

      {/* Top Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <FileMenu />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, ml: 2 }}>
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
