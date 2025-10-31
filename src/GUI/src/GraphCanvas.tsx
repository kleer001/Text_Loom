// Graph Canvas - React Flow visualization of workspace

import React, { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from '@xyflow/react';
import type { Node, Edge, NodeChange, Connection } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CustomNode } from './CustomNode';
import { useWorkspace } from './WorkspaceContext';
import { DeleteConfirmDialog } from './DeleteConfirmDialog';
import { connectionsToEdges } from './utils/edgeMapping';
import { apiClient } from './apiClient';
import type { NodeResponse, ConnectionRequest, ConnectionDeleteRequest } from './types';

const nodeTypes = {
  custom: CustomNode,
};

interface GraphCanvasProps {
  onSelectionChange?: (nodes: Node[]) => void;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ onSelectionChange }) => {
  const {
    nodes: workspaceNodes,
    connections,
    updateNode,
    deleteNodes,
    loadWorkspace,
  } = useWorkspace();
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);
  const [_isDragging, setIsDragging] = useState(false);
  const [draggedNodeIds, setDraggedNodeIds] = useState<Set<string>>(new Set());

  // Wrapped onNodesChange to prevent deselection after drag
  //
  // Why this is needed:
  // - When a node is dragged, onNodeDragStop calls updateNode()
  // - This updates workspaceNodes, triggering the workspace sync useEffect
  // - The useEffect calls setNodes(), which triggers React Flow's internal state
  // - React Flow then sends a deselection change (select: false) through onNodesChange
  // - This is a known quirk of using setNodes with useNodesState
  //
  // We intercept and filter out these deselection changes for recently dragged nodes.
  const onNodesChange = useCallback((changes: NodeChange<Node>[]) => {
    console.log('[onNodesChange]', changes);

    // Filter out deselection changes for nodes that were just dragged
    const filteredChanges = changes.filter(change => {
      if (change.type === 'select' && !change.selected && draggedNodeIds.has(change.id)) {
        console.log('[INTERCEPTED] Preventing deselection of dragged node:', change.id);
        return false; // Filter out this deselection
      }
      return true;
    });

    // Clear dragged nodes tracking after processing changes
    if (filteredChanges.length < changes.length) {
      setTimeout(() => setDraggedNodeIds(new Set()), 100);
    }

    onNodesChangeInternal(filteredChanges);
  }, [onNodesChangeInternal, draggedNodeIds]);

  // Convert workspace nodes to React Flow nodes
  useEffect(() => {
    setNodes(prevNodes =>
      workspaceNodes.map((node: NodeResponse) => {
        const nodeId = String(node.session_id);
        const existingNode = prevNodes.find(n => n.id === nodeId);

        return {
          id: nodeId,
          type: 'custom',
          position: { x: node.position[0], y: node.position[1] },
          data: { node },
          selected: existingNode?.selected ?? false,
        };
      })
    );
  }, [workspaceNodes, setNodes]);

  // Convert connections to React Flow edges
  useEffect(() => {
    const flowEdges = connectionsToEdges(connections, {
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#888', strokeWidth: 2 },
    });
    setEdges(flowEdges);
  }, [connections, setEdges]);

  // Handle selection changes from React Flow
  const handleSelectionChange = useCallback(
    (params: { nodes: Node[]; edges: Edge[] }) => {
      setSelectedNodes(params.nodes);
      onSelectionChange?.(params.nodes);
    },
    [onSelectionChange]
  );

  // Handle node drag start - track dragged node
  const onNodeDragStart = useCallback(
    (_event: unknown, node: Node) => {
      console.log('Node drag start:', node.id);
      setIsDragging(true);
      setDraggedNodeIds(new Set([node.id]));
    },
    []
  );

  // Handle node drag end - save position to backend
  const onNodeDragStop = useCallback(
    async (_event: unknown, node: Node) => {
      console.log('Node drag stop:', node.id);
      const sessionId = node.id;
      const newPosition: [number, number] = [node.position.x, node.position.y];

      try {
        await updateNode(sessionId, { position: newPosition });
      } catch (error) {
        console.error('Failed to update node position:', sessionId, error);
      }

      setIsDragging(false);
      // Keep draggedNodeIds set for a moment to intercept deselection
    },
    [updateNode]
  );

  // Handle selection drag start - track dragged nodes
  const onSelectionDragStart = useCallback(
    (_event: unknown, draggedNodes: Node[]) => {
      console.log('Selection drag start:', draggedNodes.map(n => n.id));
      setIsDragging(true);
      setDraggedNodeIds(new Set(draggedNodes.map(n => n.id)));
    },
    []
  );

  // Handle selection drag end - save positions to backend
  const onSelectionDragStop = useCallback(
    async (_event: unknown, draggedNodes: Node[]) => {
      console.log('Selection drag stop:', draggedNodes.map(n => n.id));
      try {
        await Promise.all(
          draggedNodes.map(node => {
            const sessionId = node.id;
            const newPosition: [number, number] = [node.position.x, node.position.y];
            return updateNode(sessionId, { position: newPosition });
          })
        );
      } catch (error) {
        console.error('Failed to update nodes positions:', error);
      }

      setIsDragging(false);
      // Keep draggedNodeIds set for a moment to intercept deselection
    },
    [updateNode]
  );

  // Handle delete confirmation
  const handleDeleteConfirm = useCallback(async () => {
    setDeleteDialogOpen(false);
    try {
      const nodeIds = selectedNodes.map(n => n.id);
      await deleteNodes(nodeIds);
      setSelectedNodes([]);
    } catch (error) {
      console.error('Failed to delete nodes:', error);
    }
  }, [deleteNodes, selectedNodes]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  // Handle creating connections (Phase 3.4)
  const onConnect = useCallback(async (connection: Connection) => {
    // 1. Parse handle IDs to get socket indices
    const sourceOutputIndex = parseInt(connection.sourceHandle?.replace('output-', '') || '0');
    const targetInputIndex = parseInt(connection.targetHandle?.replace('input-', '') || '0');

    // 2. Find node data to get paths
    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);

    if (!sourceNode || !targetNode) {
      console.error('Source or target node not found');
      return;
    }

    // 3. Build API request
    const request: ConnectionRequest = {
      source_node_path: (sourceNode.data as { node: NodeResponse }).node.path,
      source_output_index: sourceOutputIndex,
      target_node_path: (targetNode.data as { node: NodeResponse }).node.path,
      target_input_index: targetInputIndex,
    };

    try {
      // 4. Call backend API
      const newConnection = await apiClient.createConnection(request);

      // 5. Update edges state
      setEdges(prevEdges => {
        // Remove any existing edge to same target input
        // (backend auto-replaces, so we mirror that behavior)
        const filtered = prevEdges.filter(e =>
          !(e.target === connection.target &&
            e.targetHandle === connection.targetHandle)
        );

        // Add new edge
        const newEdge: Edge = {
          id: `${newConnection.source_node_session_id}-${newConnection.source_output_index}-${newConnection.target_node_session_id}-${newConnection.target_input_index}`,
          source: connection.source,
          target: connection.target,
          sourceHandle: connection.sourceHandle!,
          targetHandle: connection.targetHandle!,
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#888', strokeWidth: 2 },
        };

        return [...filtered, newEdge];
      });

      // 6. Refresh workspace to sync node states
      await loadWorkspace();

    } catch (error) {
      console.error('Failed to create connection:', error);
      // TODO: Show error notification to user
    }
  }, [nodes, setEdges, loadWorkspace]);

  // Handle deleting connections (Phase 3.4)
  const onEdgesDelete = useCallback(async (edgesToDelete: Edge[]) => {
    // Delete connections sequentially (backend processes one at a time)
    for (const edge of edgesToDelete) {
      // 1. Parse handle IDs to get socket indices
      const sourceOutputIndex = parseInt(edge.sourceHandle?.replace('output-', '') || '0');
      const targetInputIndex = parseInt(edge.targetHandle?.replace('input-', '') || '0');

      // 2. Find node data to get paths
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);

      if (!sourceNode || !targetNode) {
        console.warn('Source or target node not found for edge:', edge.id);
        continue; // Skip this edge
      }

      // 3. Build API request
      const request: ConnectionDeleteRequest = {
        source_node_path: (sourceNode.data as { node: NodeResponse }).node.path,
        source_output_index: sourceOutputIndex,
        target_node_path: (targetNode.data as { node: NodeResponse }).node.path,
        target_input_index: targetInputIndex,
      };

      try {
        // 4. Call backend API
        await apiClient.deleteConnection(request);

      } catch (error) {
        console.error('Failed to delete connection:', error);
        // TODO: Show error notification
        // Continue to next edge even if this one fails
      }
    }

    // 5. Remove edges from state
    setEdges(prevEdges =>
      prevEdges.filter(e => !edgesToDelete.includes(e))
    );

    // 6. Refresh workspace to sync node states
    await loadWorkspace();

  }, [nodes, setEdges, loadWorkspace]);

  // Validate connections before allowing them (Phase 3.4)
  const isValidConnection = useCallback((connection: Edge | Connection) => {
    // Prevent self-connections
    if (connection.source === connection.target) {
      console.warn('Cannot connect node to itself');
      return false;
    }

    return true; // Allow connection
  }, []);

  // Handle keyboard shortcuts (moved here to use onEdgesDelete)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input field
      const target = event.target as HTMLElement;
      const isInputField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';

      // Delete key
      if (event.key === 'Delete' || event.key === 'Backspace') {
        // Prevent default browser behavior (e.g., going back)
        if (event.key === 'Backspace' && !isInputField) {
          event.preventDefault();
        }

        // Only delete if nodes are selected and not typing
        if (selectedNodes.length > 0 && !isInputField) {
          event.preventDefault();
          setDeleteDialogOpen(true);
        }
        // Handle edge deletion (Phase 3.4)
        else if (!isInputField) {
          // Get selected edges from React Flow
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

  return (
    <>
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
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        selectNodesOnDrag={false}
        nodeDragThreshold={10}
        multiSelectionKeyCode="Shift"
        deleteKeyCode={null}
        selectionKeyCode="Shift"
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />
      </ReactFlow>
    </>
  );
};
