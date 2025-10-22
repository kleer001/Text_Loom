// src/GUI/components/layout/MainLayout.tsx

import { Box } from '@mui/material';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from 'react-resizable-panels';
import { NodePalette } from '../palette/NodePalette';
import { NodeGraph } from '../graph/NodeGraph';
import { ParameterPanel } from '../parameters/ParameterPanel';
import { OutputPanel } from '../output/OutputPanel';

export const MainLayout = () => {
  return (
    <Box sx={{ height: '100vh', display: 'flex' }}>
      <NodePalette />
      
      <ResizablePanelGroup direction="horizontal" style={{ flex: 1 }}>
        <ResizablePanel defaultSize={60} minSize={30}>
          <NodeGraph />
        </ResizablePanel>
        
        <ResizableHandle style={{ width: '4px', background: '#ddd' }} />
        
        <ResizablePanel defaultSize={25} minSize={15}>
          <ParameterPanel />
        </ResizablePanel>
        
        <ResizableHandle style={{ width: '4px', background: '#ddd' }} />
        
        <ResizablePanel defaultSize={15} minSize={10}>
          <OutputPanel />
        </ResizablePanel>
      </ResizablePanelGroup>
    </Box>
  );
};