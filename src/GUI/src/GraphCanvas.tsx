import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  BackgroundVariant,
} from '@xyflow/react';
import type { Node, Edge, NodeChange, Connection, ReactFlowInstance } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CustomNode } from './CustomNode';
import { useWorkspace } from './WorkspaceContext';
import { DeleteConfirmDialog } from './DeleteConfirmDialog';
import { connectionsToEdges } from './utils/edgeMapping';
import { transformConnectionNodeIds, enrichNodesWithConnectionState } from './utils/looperConnections';
import { gatherBoundaryNodes } from './utils/looperBoundary';
import { apiClient } from './apiClient';
import type { NodeResponse, ConnectionRequest, ParameterInfo } from './types';
import { DESELECTION_DELAY_MS } from './constants';
import { transformLooperNodes, type LooperSystem, getOriginalNodeId } from './looperTransform';
import { LoopBoundary } from './LoopBoundary';
import { useTheme } from './ThemeContext';
import { useNodePreferences } from './NodePreferencesContext';
import * as design from './nodeDesign';

const nodeTypes = {
  custom: CustomNode,
};

interface GraphCanvasProps {
  onNodeFocus?: (node: NodeResponse | null) => void;
}

const GraphCanvasInner: React.FC<GraphCanvasProps> = ({ onNodeFocus }) => {
  const { mode } = useTheme();
  const { nodeSize } = useNodePreferences();
  const colors = useMemo(() => design.getColors(mode), [mode]);
  const {
    nodes: workspaceNodes,
    connections,
    updateNode,
    deleteNodes,
    loadWorkspace,
    executingNodeId,
    newlyCreatedNodeId,
  } = useWorkspace();
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);
  const [_isDragging, setIsDragging] = useState(false);
  const [draggedNodeIds, setDraggedNodeIds] = useState<Set<string>>(new Set());
  const [looperSystems, setLooperSystems] = useState<Map<string, LooperSystem>>(new Map());
  const selectedNodeIdsRef = useRef<Set<string>>(new Set());
  const reactFlowInstanceRef = useRef<ReactFlowInstance | null>(null);
  const viewportRef = useRef<{ x: number; y: number; zoom: number } | null>(null);
  const nodeDataCacheRef = useRef<Map<string, { node: NodeResponse; size: 'large' | 'medium' | 'small'; onBypassToggle: (sessionId: string) => void; onDisplayToggle: (sessionId: string) => void }>>(new Map());

  const defaultEdgeConfig = useMemo(() => ({
    type: 'smoothstep' as const,
    animated: false,
    style: {
      stroke: colors.edge.default,
      strokeWidth: design.EDGE_WIDTH_DEFAULT
    },
  }), [colors.edge.default]);

  const edgeStyles = useMemo(() => `
    .react-flow__edge:hover .react-flow__edge-path {
      stroke: ${colors.edge.hover} !important;
      stroke-width: ${design.EDGE_WIDTH_HOVER};
    }
    .react-flow__edge.selected .react-flow__edge-path {
      stroke: ${colors.edge.selected} !important;
      stroke-width: ${design.EDGE_WIDTH_SELECTED};
    }
  `, [colors.edge.hover, colors.edge.selected]);

  const shouldPreventDeselection = useCallback((change: NodeChange<Node>): boolean => {
    if (change.type !== 'select' || change.selected) return false;
    return draggedNodeIds.has(change.id) || (executingNodeId === change.id);
  }, [draggedNodeIds, executingNodeId]);

  const extractParameterValues = useCallback((node: NodeResponse) =>
    Object.fromEntries(
      Object.entries(node.parameters || {}).map(([key, param]) =>
        [key, (param as ParameterInfo).value]
      )
    ), []);

  const handleBypassToggle = useCallback(async (sessionId: string) => {
    const targetNodeId = getOriginalNodeId(sessionId);
    const node = workspaceNodes.find(n => n.session_id === targetNodeId);
    if (!node) return;

    const currentBypass = node.parameters?.bypass?.value === true;
    await updateNode(targetNodeId, {
      parameters: { ...extractParameterValues(node), bypass: !currentBypass }
    });
  }, [workspaceNodes, updateNode, extractParameterValues]);

  const handleDisplayToggle = useCallback(async (sessionId: string) => {
    const targetNodeId = getOriginalNodeId(sessionId);
    const node = workspaceNodes.find(n => n.session_id === targetNodeId);
    if (!node) return;

    const currentDisplay = node.parameters?.display?.value === true;

    if (!currentDisplay) {
      const otherNodesWithDisplay = workspaceNodes.filter(
        n => n.session_id !== targetNodeId && n.parameters?.display?.value === true
      );

      await Promise.all(
        otherNodesWithDisplay.map(otherNode =>
          updateNode(otherNode.session_id, {
            parameters: { ...extractParameterValues(otherNode), display: false }
          })
        )
      );
    }

    await updateNode(targetNodeId, {
      parameters: { ...extractParameterValues(node), display: !currentDisplay }
    });
  }, [workspaceNodes, updateNode, extractParameterValues]);

  const onNodesChange = useCallback((changes: NodeChange<Node>[]) => {
    const filteredChanges = changes.filter(change => !shouldPreventDeselection(change));

    if (filteredChanges.length < changes.length) {
      setTimeout(() => setDraggedNodeIds(new Set()), DESELECTION_DELAY_MS);
    }

    onNodesChangeInternal(filteredChanges);
  }, [onNodesChangeInternal, shouldPreventDeselection]);

  useLayoutEffect(() => {
    // Save current viewport before transformation
    // COMMENTED OUT THE FOLLOWING 3 lines to attempt to fix flickering
    // if (reactFlowInstanceRef.current) {
    //   viewportRef.current = reactFlowInstanceRef.current.getViewport();
    // }

    const { displayNodes, looperSystems: systems } = transformLooperNodes(workspaceNodes);
    setLooperSystems(systems);

    const transformedConnections = transformConnectionNodeIds(connections, systems);
    const enrichedNodes = enrichNodesWithConnectionState(displayNodes, transformedConnections);
    const currentlySelectedIds = selectedNodeIdsRef.current;

    const newNodes = enrichedNodes.map((node: NodeResponse) => {
      const nodeId = String(node.session_id);

      // Get or create cached data object to prevent recreation on every render
      let dataObj = nodeDataCacheRef.current.get(nodeId);
      if (!dataObj || dataObj.node !== node || dataObj.onBypassToggle !== handleBypassToggle || dataObj.onDisplayToggle !== handleDisplayToggle || dataObj.size !== nodeSize) {
        dataObj = { node, size: nodeSize, onBypassToggle: handleBypassToggle, onDisplayToggle: handleDisplayToggle };
        nodeDataCacheRef.current.set(nodeId, dataObj);
      }

      return {
        id: nodeId,
        type: 'custom',
        position: { x: node.position[0], y: node.position[1] },
        data: dataObj,
        selected: nodeId === newlyCreatedNodeId || currentlySelectedIds.has(nodeId),
      };
    });

    // Clean up cache for deleted nodes
    const currentNodeIds = new Set(newNodes.map(n => n.id));
    for (const cachedId of nodeDataCacheRef.current.keys()) {
      if (!currentNodeIds.has(cachedId)) {
        nodeDataCacheRef.current.delete(cachedId);
      }
    }

    setNodes(newNodes);
    setEdges(connectionsToEdges(transformedConnections, defaultEdgeConfig));

    // Restore viewport after state updates
    // COMMENTED OUT TO 193 To try and fix refreshing blinking issue
    // if (viewportRef.current && reactFlowInstanceRef.current) {
    //   const savedViewport = viewportRef.current;
    //   // Use multiple attempts to ensure restoration
    //   requestAnimationFrame(() => {
    //     reactFlowInstanceRef.current?.setViewport(savedViewport, { duration: 0 });
    //   });
    //   setTimeout(() => {
    //     reactFlowInstanceRef.current?.setViewport(savedViewport, { duration: 0 });
    //   }, 0);
    // }

    if (newlyCreatedNodeId) {
      const newNode = enrichedNodes.find((n: NodeResponse) => String(n.session_id) === newlyCreatedNodeId);
      if (newNode && onNodeFocus) {
        onNodeFocus(newNode);
      }
    }
  }, [workspaceNodes, connections, setNodes, setEdges, newlyCreatedNodeId, onNodeFocus, handleBypassToggle, handleDisplayToggle, defaultEdgeConfig, nodeSize]);

  const handleSelectionChange = useCallback(
    (params: { nodes: Node[]; edges: Edge[] }) => {
      setSelectedNodes(params.nodes);
      selectedNodeIdsRef.current = new Set(params.nodes.map(n => n.id));

      if (params.nodes.length > 0 && onNodeFocus) {
        const focusedReactFlowNode = params.nodes[0];
        const nodeData = focusedReactFlowNode.data as { node: NodeResponse };
        onNodeFocus(nodeData.node);
      }
    },
    [onNodeFocus]
  );

  const onNodeDragStart = useCallback(
    (_event: unknown, node: Node) => {
      setIsDragging(true);
      setDraggedNodeIds(new Set([node.id]));
    },
    []
  );

  const onNodeDragStop = useCallback(
    async (_event: unknown, node: Node) => {
      const newPosition: [number, number] = [node.position.x, node.position.y];
      const nodeData = node.data as { node: NodeResponse };
      const nodeType = nodeData.node.type;

      // For looper_start/end, update the actual child node (inputNull/outputNull)
      // For regular nodes, update the node itself
      let targetNodeId: string;

      if (nodeType === 'looper_start') {
        // Find inputNull for this looper
        const looperId = getOriginalNodeId(node.id);
        const looperSystem = looperSystems.get(looperId);
        targetNodeId = looperSystem?.inputNullNode.session_id || node.id;
      } else if (nodeType === 'looper_end') {
        // Find outputNull for this looper
        const looperId = getOriginalNodeId(node.id);
        const looperSystem = looperSystems.get(looperId);
        targetNodeId = looperSystem?.outputNullNode.session_id || node.id;
      } else {
        targetNodeId = node.id;
      }

      try {
        await updateNode(targetNodeId, { position: newPosition });
      } catch (error) {
        console.error('Failed to update node position:', node.id, error);
      }

      setIsDragging(false);
    },
    [updateNode, looperSystems]
  );

  const onSelectionDragStart = useCallback(
    (_event: unknown, draggedNodes: Node[]) => {
      setIsDragging(true);
      setDraggedNodeIds(new Set(draggedNodes.map(n => n.id)));
    },
    []
  );

  const onSelectionDragStop = useCallback(
    async (_event: unknown, draggedNodes: Node[]) => {
      try {
        await Promise.all(
          draggedNodes.map(node => {
            const newPosition: [number, number] = [node.position.x, node.position.y];
            const nodeData = node.data as { node: NodeResponse };
            const nodeType = nodeData.node.type;

            let targetNodeId: string;

            if (nodeType === 'looper_start') {
              const looperId = getOriginalNodeId(node.id);
              const looperSystem = looperSystems.get(looperId);
              targetNodeId = looperSystem?.inputNullNode.session_id || node.id;
            } else if (nodeType === 'looper_end') {
              const looperId = getOriginalNodeId(node.id);
              const looperSystem = looperSystems.get(looperId);
              targetNodeId = looperSystem?.outputNullNode.session_id || node.id;
            } else {
              targetNodeId = node.id;
            }

            return updateNode(targetNodeId, { position: newPosition });
          })
        );
      } catch (error) {
        console.error('Failed to update nodes positions:', error);
      }

      setIsDragging(false);
    },
    [updateNode, looperSystems]
  );

  const handleDeleteConfirm = useCallback(async () => {
    setDeleteDialogOpen(false);
    try {
      const nodeIds = selectedNodes.map(n => getOriginalNodeId(n.id));
      const uniqueNodeIds = Array.from(new Set(nodeIds));
      await deleteNodes(uniqueNodeIds);
      setSelectedNodes([]);
      selectedNodeIdsRef.current = new Set();
    } catch (error) {
      console.error('Failed to delete nodes:', error);
    }
  }, [deleteNodes, selectedNodes]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  const onConnect = useCallback(async (connection: Connection) => {
    const sourceOutputIndex = parseInt(connection.sourceHandle?.replace('output-', '') || '0');
    const targetInputIndex = parseInt(connection.targetHandle?.replace('input-', '') || '0');

    if (isNaN(sourceOutputIndex) || isNaN(targetInputIndex)) {
      console.error('Failed to parse connection indices');
      return;
    }

    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);

    if (!sourceNode || !targetNode) {
      console.error('Source or target node not found');
      return;
    }

    const request: ConnectionRequest = {
      source_node_path: (sourceNode.data as { node: NodeResponse }).node.path,
      source_output_index: sourceOutputIndex,
      target_node_path: (targetNode.data as { node: NodeResponse }).node.path,
      target_input_index: targetInputIndex,
    };

    try {
      const newConnection = await apiClient.createConnection(request);

      setEdges(prevEdges => {
        const filtered = prevEdges.filter(e =>
          !(e.target === connection.target &&
            e.targetHandle === connection.targetHandle)
        );

        const newEdge: Edge = {
          id: newConnection.connection_id,
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle!,
          targetHandle: connection.targetHandle!,
          ...defaultEdgeConfig,
        };

        return [...filtered, newEdge];
      });

      await loadWorkspace();
    } catch (error) {
      console.error('Failed to create connection:', error);
    }
  }, [nodes, setEdges, loadWorkspace, defaultEdgeConfig]);

  const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
    for (const edge of edgesToDelete) {
      try {
        await apiClient.deleteConnectionById(edge.id);
      } catch (error) {
        console.error('Failed to delete connection:', error);
      }
    }

    setEdges(prevEdges =>
      prevEdges.filter(e => !edgesToDelete.includes(e))
    );

    await loadWorkspace();
  }, [setEdges, loadWorkspace]);

  const isValidConnection = useCallback((connection: Edge | Connection) => {
    if (connection.source === connection.target) {
      console.warn('Cannot connect node to itself');
      return false;
    }
    return true;
  }, []);

  useEffect(() => {
    console.log('GraphCanvas MOUNTED');
    return () => console.log('GraphCanvas UNMOUNTED');
  }, []);   

  useLayoutEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      const isInputField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';

      if (event.key === 'Delete' || event.key === 'Backspace') {
        if (event.key === 'Backspace' && !isInputField) {
          event.preventDefault();
        }

        if (selectedNodes.length > 0 && !isInputField) {
          event.preventDefault();
          setDeleteDialogOpen(true);
        } else if (!isInputField) {
          const selectedEdges = edges.filter(e => e.selected);
          if (selectedEdges.length > 0) {
            event.preventDefault();
            onEdgesDelete(selectedEdges);
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNodes, edges, onEdgesDelete]);

  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstanceRef.current = instance;
    // Initialize viewport ref with current state
    viewportRef.current = instance.getViewport();
  }, []);
// COMMENTED OUT To try and fix blinking issue
//   const onMove = useCallback(() => {
//     // Continuously track viewport changes
//     if (reactFlowInstanceRef.current) {
//       viewportRef.current = reactFlowInstanceRef.current.getViewport();
//     }
//   }, []);

  // Handle custom events from MenuBar for edit operations
  useLayoutEffect(() => {
    const handleSelectAll = () => {
      if (reactFlowInstanceRef.current) {
        const allNodes = reactFlowInstanceRef.current.getNodes();
        const allEdges = reactFlowInstanceRef.current.getEdges();
        setNodes(allNodes.map(n => ({ ...n, selected: true })));
        setEdges(allEdges.map(e => ({ ...e, selected: true })));
        setSelectedNodes(allNodes);
        selectedNodeIdsRef.current = new Set(allNodes.map(n => n.id));
      }
    };

    const handleDeleteSelected = () => {
      if (selectedNodes.length > 0) {
        setDeleteDialogOpen(true);
      }
    };

    const handleCopy = () => {
      if (selectedNodes.length > 0) {
        const nodesToCopy = selectedNodes.map(n => {
          const nodeData = (n.data as { node: NodeResponse }).node;
          return {
            type: nodeData.type,
            name: nodeData.name,
            parameters: nodeData.parameters,
            position: nodeData.position,
          };
        });
        // Store in window for cross-component access
        (window as any).__textloom_clipboard = {
          nodes: nodesToCopy,
          timestamp: Date.now(),
        };
        console.log(`Copied ${nodesToCopy.length} node(s)`);
      }
    };

    const handleCut = () => {
      handleCopy();
      if (selectedNodes.length > 0) {
        setDeleteDialogOpen(true);
      }
    };

    const handlePaste = async () => {
      const clipboard = (window as any).__textloom_clipboard;
      if (!clipboard || !clipboard.nodes || clipboard.nodes.length === 0) {
        console.log('Nothing to paste');
        return;
      }

      try {
        // Disable undo tracking during paste operations
        await apiClient.disableUndo();

        const offset = 50; // Offset for pasted nodes
        for (const nodeData of clipboard.nodes) {
          const newPosition: [number, number] = [
            nodeData.position[0] + offset,
            nodeData.position[1] + offset,
          ];

          // Create new node via API - backend handles duplicate names automatically
          const createRequest = {
            type: nodeData.type,
            name: nodeData.name,
            parent_path: '/',
            position: newPosition,
          };

          const newNodes = await apiClient.createNode(createRequest);

          // Update parameters if any
          if (newNodes.length > 0 && nodeData.parameters) {
            const paramValues: Record<string, any> = {};
            for (const [key, param] of Object.entries(nodeData.parameters)) {
              if (key !== 'bypass' && key !== 'display') {
                paramValues[key] = (param as any).value;
              }
            }
            if (Object.keys(paramValues).length > 0) {
              await apiClient.updateNode(newNodes[0].session_id, { parameters: paramValues });
            }
          }
        }

        // Re-enable undo tracking
        await apiClient.enableUndo();

        // Update clipboard positions for subsequent pastes
        (window as any).__textloom_clipboard.nodes = clipboard.nodes.map((n: any) => ({
          ...n,
          position: [n.position[0] + offset, n.position[1] + offset],
        }));

        await loadWorkspace();
        console.log(`Pasted ${clipboard.nodes.length} node(s)`);
      } catch (error) {
        console.error('Paste failed:', error);
        // Always re-enable undo tracking even on error
        try {
          await apiClient.enableUndo();
        } catch (enableError) {
          console.error('Failed to re-enable undo:', enableError);
        }
      }
    };

    const handleDuplicate = async () => {
      if (selectedNodes.length > 0) {
        handleCopy();
        await handlePaste();
      }
    };

    window.addEventListener('textloom:selectAll', handleSelectAll);
    window.addEventListener('textloom:deleteSelected', handleDeleteSelected);
    window.addEventListener('textloom:copy', handleCopy);
    window.addEventListener('textloom:cut', handleCut);
    window.addEventListener('textloom:paste', handlePaste);
    window.addEventListener('textloom:duplicate', handleDuplicate);

    return () => {
      window.removeEventListener('textloom:selectAll', handleSelectAll);
      window.removeEventListener('textloom:deleteSelected', handleDeleteSelected);
      window.removeEventListener('textloom:copy', handleCopy);
      window.removeEventListener('textloom:cut', handleCut);
      window.removeEventListener('textloom:paste', handlePaste);
      window.removeEventListener('textloom:duplicate', handleDuplicate);
    };
  }, [selectedNodes, setNodes, setEdges, loadWorkspace]);

  return (
    <>
      <style>{edgeStyles}</style>
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        nodeCount={selectedNodes.length}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onSelectionChange={handleSelectionChange}
        onNodeDragStart={onNodeDragStart}
        onNodeDragStop={onNodeDragStop}
        onSelectionDragStart={onSelectionDragStart}
        onSelectionDragStop={onSelectionDragStop}
        onConnect={onConnect}
        onEdgesDelete={onEdgesDelete}
        isValidConnection={isValidConnection}
        nodeTypes={nodeTypes}
        onInit={onInit}
        //onMove={onMove}
        fitView={false}
        minZoom={0.1}
        maxZoom={2}
        selectNodesOnDrag={false}
        nodeDragThreshold={10}
        multiSelectionKeyCode="Shift"
        deleteKeyCode={null}
        selectionKeyCode="Shift"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={12}
          size={1}
          color={colors.canvas.grid}
          style={{ backgroundColor: colors.canvas.background }}
        />
        <Controls />
        {Array.from(looperSystems.values()).map(system => {
          const transformedConnections = transformConnectionNodeIds(connections, looperSystems);
          return (
            <LoopBoundary
              key={system.looperNode.session_id}
              nodes={gatherBoundaryNodes(system, workspaceNodes, nodes, transformedConnections)}
            />
          );
        })}
      </ReactFlow>
    </>
  );
};

export const GraphCanvas: React.FC<GraphCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
};
