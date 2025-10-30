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
import type { Node, Edge } from '@xyflow/react';
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
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node[]>([]);

  // Convert workspace nodes to React Flow nodes
  useEffect(() => {
    const flowNodes: Node[] = workspaceNodes.map((node: NodeResponse) => {
      const nodeId = String(node.session_id);

      return {
        id: nodeId,
        type: 'custom',
        position: { x: node.position[0], y: node.position[1] },
        data: { node },
      };
    });

    setNodes(flowNodes);
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
      console.log('[SELECTION]', {
        nodeCount: params.nodes.length,
        nodeIds: params.nodes.map(n => n.id)
      });
      setSelectedNodes(params.nodes);
      onSelectionChange?.(params.nodes);
    },
    [onSelectionChange]
  );

  // Handle node drag end - save position to backend
  const onNodeDragStop = useCallback(
    async (_event: unknown, node: Node) => {
      console.log('[DRAG-END]', { node: node.id, pos: node.position });
      const sessionId = node.id;
      const newPosition: [number, number] = [node.position.x, node.position.y];

      try {
        await updateNode(sessionId, { position: newPosition });
      } catch (error) {
        console.error('[DRAG-END-ERROR]', sessionId, error);
      }
    },
    [updateNode]
  );

  // Handle selection drag end - save positions to backend
  const onSelectionDragStop = useCallback(
    async (_event: unknown, draggedNodes: Node[]) => {
      console.log('[MULTI-DRAG-END]', {
        count: draggedNodes.length,
        nodes: draggedNodes.map(n => n.id)
      });

      try {
        await Promise.all(
          draggedNodes.map(node => {
            const sessionId = node.id;
            const newPosition: [number, number] = [node.position.x, node.position.y];
            return updateNode(sessionId, { position: newPosition });
          })
        );
      } catch (error) {
        console.error('[MULTI-DRAG-END-ERROR]', error);
      }
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
        onNodeDragStop={onNodeDragStop}
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
