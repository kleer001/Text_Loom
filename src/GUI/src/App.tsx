// Main App Component - Application shell with layout

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import PublicIcon from '@mui/icons-material/Public';
import { WorkspaceProvider, useWorkspace } from './WorkspaceContext';
import { GraphCanvas } from './GraphCanvas';
import { NodeDetailsPanel } from './NodeDetailsPanel';
import { GlobalsPanel } from './GlobalsPanel';
import { AddNodeMenu } from './AddNodeMenu';
import { OutputPanel } from './OutputPanel';
import { MenuBar } from './MenuBar';
import { KeyboardShortcutsDialog } from './KeyboardShortcutsDialog';
import { AboutDialog } from './AboutDialog';
import { AutosaveRecoveryDialog } from './AutosaveRecoveryDialog';
import { useFileManager } from './hooks/useFileManager';
import { fileManager } from './services/fileManager';
import { apiClient } from './apiClient';
import type { NodeResponse } from './types';
import { isLooperPart, getOriginalNodeId } from './looperTransform';

const AppContent: React.FC = () => {
  const { nodes, loadWorkspace, loading, error, lastExecutionResult, lastExecutedNodeName, clearExecutionResult } = useWorkspace();
  const { save, saveAs, open, newWorkspace, isDirty, markClean } = useFileManager();
  const [focusedNode, setFocusedNode] = useState<NodeResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'globals'>('details');
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
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

  useEffect(() => {
    if (focusedNode) {
      if (isLooperPart(focusedNode.type)) {
        const originalId = getOriginalNodeId(focusedNode.session_id);
        const originalNode = nodes.find(n => n.session_id === originalId);
        if (!originalNode) {
          setFocusedNode(null);
        } else if (
          originalNode.name !== focusedNode.name ||
          originalNode.parameters !== focusedNode.parameters ||
          originalNode.cook_count !== focusedNode.cook_count ||
          originalNode.errors !== focusedNode.errors ||
          originalNode.warnings !== focusedNode.warnings
        ) {
          setFocusedNode({
            ...focusedNode,
            name: originalNode.name,
            parameters: originalNode.parameters,
            cook_count: originalNode.cook_count,
            errors: originalNode.errors,
            warnings: originalNode.warnings,
          });
        }
      } else {
        const updatedNode = nodes.find(n => n.session_id === focusedNode.session_id);
        if (updatedNode && updatedNode !== focusedNode) {
          setFocusedNode(updatedNode);
        } else if (!updatedNode) {
          setFocusedNode(null);
        }
      }
    }
  }, [nodes, focusedNode]);

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
    const handleKeyDown = async (e: KeyboardEvent) => {
      // Check if we're in an input/textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return;
      }

      // Ctrl+S - Save
      if (e.ctrlKey && !e.shiftKey && e.key === 's') {
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

      // Ctrl+Z - Undo
      if (e.ctrlKey && !e.shiftKey && e.key === 'z') {
        e.preventDefault();
        try {
          await apiClient.undo();
          await loadWorkspace();
        } catch (err) {
          console.error('Undo failed:', err);
        }
      }

      // Ctrl+Shift+Z - Redo
      if (e.ctrlKey && e.shiftKey && e.key === 'Z') {
        e.preventDefault();
        try {
          await apiClient.redo();
          await loadWorkspace();
        } catch (err) {
          console.error('Redo failed:', err);
        }
      }

      // Ctrl+A - Select All
      if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('textloom:selectAll'));
      }

      // Ctrl+C - Copy
      if (e.ctrlKey && !e.shiftKey && e.key === 'c') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('textloom:copy'));
      }

      // Ctrl+X - Cut
      if (e.ctrlKey && e.key === 'x') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('textloom:cut'));
      }

      // Ctrl+V - Paste
      if (e.ctrlKey && e.key === 'v') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('textloom:paste'));
      }

      // Ctrl+D - Duplicate
      if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('textloom:duplicate'));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [save, saveAs, open, newWorkspace, loadWorkspace]);

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

      {/* Dialogs */}
      <KeyboardShortcutsDialog
        open={showKeyboardShortcuts}
        onClose={() => setShowKeyboardShortcuts(false)}
      />
      <AboutDialog
        open={showAbout}
        onClose={() => setShowAbout(false)}
      />

      {/* Top Navigation Bar */}
      <AppBar position="static">
        <Toolbar variant="dense">
          <MenuBar
            onKeyboardShortcuts={() => setShowKeyboardShortcuts(true)}
            onAbout={() => setShowAbout(true)}
          />
          <Box sx={{ flexGrow: 1 }} />
          <Typography variant="h6" component="div">
            TextLoom
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
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
            {loading && !error && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'transparent',
                  zIndex: 1000,
                  pointerEvents: 'none',
                }}
              >
                <CircularProgress
                  sx={{
                    pointerEvents: 'auto',
                    color: 'primary.main',
                  }}
                  size={60}
                />
              </Box>
            )}
            <GraphCanvas onNodeFocus={setFocusedNode} />
            <AddNodeMenu variant="fab" />
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
