import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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
import * as design from './nodeDesign';

const nodeTypes = {
  custom: CustomNode,
};

interface GraphCanvasProps {
  onNodeFocus?: (node: NodeResponse | null) => void;
}

const GraphCanvasInner: React.FC<GraphCanvasProps> = ({ onNodeFocus }) => {
  const { mode } = useTheme();
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

  useEffect(() => {
    const viewport = reactFlowInstanceRef.current?.getViewport();

    const { displayNodes, looperSystems: systems } = transformLooperNodes(workspaceNodes);
    setLooperSystems(systems);

    const transformedConnections = transformConnectionNodeIds(connections, systems);
    const enrichedNodes = enrichNodesWithConnectionState(displayNodes, transformedConnections);
    const currentlySelectedIds = selectedNodeIdsRef.current;

    const newNodes = enrichedNodes.map((node: NodeResponse) => {
      const nodeId = String(node.session_id);
      return {
        id: nodeId,
        type: 'custom',
        position: { x: node.position[0], y: node.position[1] },
        data: { node, onBypassToggle: handleBypassToggle, onDisplayToggle: handleDisplayToggle },
        selected: nodeId === newlyCreatedNodeId || currentlySelectedIds.has(nodeId),
      };
    });

    setNodes(newNodes);
    setEdges(connectionsToEdges(transformedConnections, defaultEdgeConfig));

    if (viewport) {
      requestAnimationFrame(() => {
        reactFlowInstanceRef.current?.setViewport(viewport, { duration: 0 });
      });
    }

    if (newlyCreatedNodeId) {
      const newNode = enrichedNodes.find((n: NodeResponse) => String(n.session_id) === newlyCreatedNodeId);
      if (newNode && onNodeFocus) {
        onNodeFocus(newNode);
      }
    }
  }, [workspaceNodes, connections, setNodes, setEdges, newlyCreatedNodeId, onNodeFocus, handleBypassToggle, handleDisplayToggle, defaultEdgeConfig]);

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
      const originalNodeId = getOriginalNodeId(node.id);

      try {
        await updateNode(originalNodeId, { position: newPosition });
      } catch (error) {
        console.error('Failed to update node position:', node.id, error);
      }

      setIsDragging(false);
    },
    [updateNode]
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
            const originalNodeId = getOriginalNodeId(node.id);
            return updateNode(originalNodeId, { position: newPosition });
          })
        );
      } catch (error) {
        console.error('Failed to update nodes positions:', error);
      }

      setIsDragging(false);
    },
    [updateNode]
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
  }, []);

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
        fitView={false}
        fitViewOnInit={false}
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
