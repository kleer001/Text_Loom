import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { WorkspaceProvider, useWorkspace } from './contexts/WorkspaceContext';
import { SelectionProvider } from './contexts/SelectionContext';
import { NodeGraph } from './components/graph/NodeGraph';  // Named import (stays the same)
import ParameterPanel from './components/parameters/ParameterPanel';  // Default import
import OutputPanel from './components/output/OutputPanel';  // Default import
import NodePalette from './components/palette/NodePalette';  // Default import

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    success: { main: '#4caf50' },
    error: { main: '#f44336' },
    warning: { main: '#ff9800' },
  },
});

const AppContent: React.FC = () => {
  const { state, fetchWorkspace } = useWorkspace();

  return (
    <>
      <AppBar position="static" elevation={1}>
        <Toolbar variant="dense">
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            TextLoom
          </Typography>
          <Button color="inherit" onClick={fetchWorkspace} disabled={state.loading}>
            Refresh
          </Button>
          {state.error && <Typography color="error" variant="caption">{state.error}</Typography>}
        </Toolbar>
      </AppBar>

      <PanelGroup direction="horizontal" style={{ height: 'calc(100vh - 48px)' }}>
        {/* Node Graph - 60% */}
        <Panel defaultSize={60} minSize={30}>
          <div style={{ height: '100%', position: 'relative' }}>
            <NodePalette />
            <NodeGraph />
          </div>
        </Panel>

        <PanelResizeHandle style={{ width: '4px', background: '#ccc' }} />

        {/* Parameters - 25% */}
        <Panel defaultSize={25} minSize={15}>
          <ParameterPanel />
        </Panel>

        <PanelResizeHandle style={{ width: '4px', background: '#ccc' }} />

        {/* Output - 15% */}
        <Panel defaultSize={15} minSize={10}>
          <OutputPanel />
        </Panel>
      </PanelGroup>
    </>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <WorkspaceProvider>
        <SelectionProvider>
          <AppContent />
        </SelectionProvider>
      </WorkspaceProvider>
    </ThemeProvider>
  );
};

export default App;