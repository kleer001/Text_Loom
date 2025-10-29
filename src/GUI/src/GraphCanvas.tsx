// Graph Canvas - React Flow visualization of workspace

import React, { useCallback, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  type NodeChange,
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
  onRenameRequested?: () => void;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ onRenameRequested }) => {
  const {
    nodes: workspaceNodes,
    connections,
    selectNode,
    selectNodes,
    selectedNodeIds,
    updateNode,
    deleteNodes,
  } = useWorkspace();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [nodesToDelete, setNodesToDelete] = useState<number[]>([]);

  // Convert workspace nodes to React Flow nodes
  useEffect(() => {
    const flowNodes: Node[] = workspaceNodes.map((node: NodeResponse) => {
      const nodeId = String(node.session_id);
      const isSelected = selectedNodeIds.includes(nodeId);

      return {
        id: nodeId,
        type: 'custom',
        position: { x: node.position[0], y: node.position[1] },
        data: { node },
        selected: isSelected,
      };
    });

    setNodes(flowNodes);
  }, [workspaceNodes, selectedNodeIds, setNodes]);

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

  // Handle node selection (industry-standard pattern)
  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      const wasSelected = selectedNodeIds.includes(node.id);

      // DEBUG: Track click events
      console.log('[CLICK]', {
        id: node.id,
        wasSelected,
        shift: event.shiftKey,
        currentSelection: selectedNodeIds
      });

      if (event.shiftKey) {
        // Shift+click: toggle node in selection
        const newSelection = wasSelected
          ? selectedNodeIds.filter(id => id !== node.id)
          : [...selectedNodeIds, node.id];

        console.log('[MULTI-SELECT]', { from: selectedNodeIds, to: newSelection });
        selectNodes(newSelection);
      } else {
        // Regular click: select only this node (unless already selected)
        // If already selected, don't deselect (allows drag-to-move)
        if (!wasSelected) {
          console.log('[SELECT]', { node: node.id });
          selectNode(node.id);
        } else {
          console.log('[ALREADY-SELECTED]', { node: node.id, action: 'keeping selection for drag' });
        }
      }
    },
    [selectNode, selectNodes, selectedNodeIds]
  );


  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      // Filter out selection changes - we manage those ourselves
      const selectionChanges = changes.filter(c => c.type === 'select');
      const otherChanges = changes.filter(c => c.type !== 'select');

      // DEBUG: Track what React Flow is trying to do
      if (selectionChanges.length > 0) {
        console.log('[RF-SELECT-BLOCKED]', selectionChanges);
      }
      if (otherChanges.length > 0 && otherChanges.some(c => c.type === 'position')) {
        console.log('[MOVEMENT]', otherChanges.filter(c => c.type === 'position'));
      }

      onNodesChange(otherChanges);
    },
    [onNodesChange]
  );

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    console.log('[DESELECT-ALL]');
    selectNode(null);
  }, [selectNode]);

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
    async (_event: unknown, selectedNodes: Node[]) => {
      console.log('[MULTI-DRAG-END]', {
        count: selectedNodes.length,
        nodes: selectedNodes.map(n => n.id)
      });

      try {
        await Promise.all(
          selectedNodes.map(node => {
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

      // F2 key - trigger rename
      if (event.key === 'F2') {
        event.preventDefault();
        if (selectedNodeIds.length === 1 && onRenameRequested) {
          onRenameRequested();
        }
        return;
      }

      // Delete key
      if (event.key === 'Delete' || event.key === 'Backspace') {
        // Prevent default browser behavior (e.g., going back)
        if (event.key === 'Backspace' && !isInputField) {
          event.preventDefault();
        }

        // Only delete if nodes are selected and not typing
        if (selectedNodeIds.length > 0 && !isInputField) {
          event.preventDefault();
          setNodesToDelete(selectedNodeIds);
          setDeleteDialogOpen(true);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNodeIds, onRenameRequested]);

  // Handle delete confirmation
  const handleDeleteConfirm = useCallback(async () => {
    setDeleteDialogOpen(false);
    try {
      await deleteNodes(nodesToDelete);
      setNodesToDelete([]);
    } catch (error) {
      console.error('Failed to delete nodes:', error);
    }
  }, [deleteNodes, nodesToDelete]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
    setNodesToDelete([]);
  }, []);

  return (
    <>
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        nodeCount={nodesToDelete.length}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={handleNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
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
