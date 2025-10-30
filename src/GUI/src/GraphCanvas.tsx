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
import type { Node, Edge, NodeChange } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CustomNode } from './CustomNode';
import { useWorkspace } from './WorkspaceContext';
import { DeleteConfirmDialog } from './DeleteConfirmDialog';
import type { NodeResponse, ConnectionResponse } from './types';

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
  } = useWorkspace();
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNodeIds, setDraggedNodeIds] = useState<Set<string>>(new Set());

  // Wrapped onNodesChange to intercept and log changes
  const onNodesChange = useCallback((changes: NodeChange<Node>[]) => {
    console.log('Node changes:', changes);

    // Filter out deselection changes for nodes that were just dragged
    const filteredChanges = changes.filter(change => {
      if (change.type === 'select' && !change.selected && draggedNodeIds.has(change.id)) {
        console.log('Preventing deselection of dragged node:', change.id);
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
    const flowEdges: Edge[] = connections.map((conn: ConnectionResponse, idx: number) => ({
      id: `edge-${idx}`,
      source: String(conn.source_node_session_id),
      target: String(conn.target_node_session_id),
      sourceHandle: `output-${conn.source_output_index}`,
      targetHandle: `input-${conn.target_input_index}`,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#888', strokeWidth: 2 },
    }));
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

  // Handle keyboard shortcuts
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
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNodes]);

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
