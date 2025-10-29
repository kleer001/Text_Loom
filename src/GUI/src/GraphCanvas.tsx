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
    console.log('[SELECTION] Converting workspace nodes to React Flow nodes:', {
      workspaceNodesCount: workspaceNodes.length,
      selectedNodeIds,
      selectedNodeIdsCount: selectedNodeIds.length
    });

    const flowNodes: Node[] = workspaceNodes.map((node: NodeResponse) => {
      const nodeId = String(node.session_id);
      const isSelected = selectedNodeIds.includes(nodeId);

      console.log('[SELECTION] Processing node:', {
        sessionId: node.session_id,
        nodeId,
        nodeIdType: typeof nodeId,
        isSelected,
        selectedNodeIds
      });

      return {
        id: nodeId,
        type: 'custom',
        position: { x: node.position[0], y: node.position[1] },
        data: { node },
        selected: isSelected,
      };
    });

    console.log('[SELECTION] React Flow nodes created:', {
      totalNodes: flowNodes.length,
      selectedNodes: flowNodes.filter(n => n.selected).map(n => n.id)
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

  // Handle node selection// Handle node selection (industry-standard pattern)
  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      console.log('[SELECTION] onNodeClick triggered:', {
        nodeId: node.id,
        wasAlreadySelected: selectedNodeIds.includes(node.id),
        shiftKey: event.shiftKey,
      });

      if (event.shiftKey) {
        // Shift+click: toggle node in selection
        const wasSelected = selectedNodeIds.includes(node.id);
        const newSelection = wasSelected
          ? selectedNodeIds.filter(id => id !== node.id)
          : [...selectedNodeIds, node.id];
        selectNodes(newSelection);
      } else {
        // Regular click: select only this node (unless already selected)
        // If already selected, don't deselect (allows drag-to-move)
        if (!selectedNodeIds.includes(node.id)) {
          selectNode(node.id);
        }
      }
    },
    [selectNode, selectNodes, selectedNodeIds]
  );


const handleNodesChange = useCallback(
  (changes: NodeChange[]) => {
    // Filter out selection changes - we manage those ourselves
    const filteredChanges = changes.filter(
      change => change.type !== 'select'
    );
    onNodesChange(filteredChanges);
  },
  [onNodesChange]
);

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    console.log('[SELECTION] onPaneClick - deselecting all nodes');
    selectNode(null);
  }, [selectNode]);

  // Handle node drag end - save position to backend
  const onNodeDragStop = useCallback(
    async (_event: unknown, node: Node) => {
      const sessionId = node.id;
      const newPosition: [number, number] = [node.position.x, node.position.y];

      try {
        await updateNode(sessionId, { position: newPosition });
      } catch (error) {
        console.error('Failed to save node position for session_id:', sessionId, error);
      }
    },
    [updateNode]
  );

  // Handle selection drag end - save positions to backend
  const onSelectionDragStop = useCallback(
    async (_event: unknown, selectedNodes: Node[]) => {
      try {
        await Promise.all(
          selectedNodes.map(node => {
            const sessionId = node.id;
            const newPosition: [number, number] = [node.position.x, node.position.y];
            return updateNode(sessionId, { position: newPosition });
          })
        );
      } catch (error) {
        console.error('Failed to save node positions:', error);
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
            onNodesChange={onNodesChange}
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
            nodeDragThreshold={10}  // ADD THIS LINE - 10px threshold before drag starts
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
