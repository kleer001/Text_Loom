// src/GUI/src/components/graph/NodeGraph.tsx

import { useCallback, useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  OnConnect, 
  OnNodeDrag,
  Node as RFNode,
  Edge as RFEdge,
} from 'reactflow';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { useSelection } from '../../contexts/SelectionContext';
import CustomNode from './nodes/CustomNode';
import 'reactflow/dist/style.css';

const nodeTypes = {
  default: CustomNode,
};

export const NodeGraph = () => {
  const { state, createConnection, updateNodePosition, createNode } = useWorkspace();
  const { selectNode } = useSelection();

  const nodes: RFNode[] = useMemo(() => 
    state.nodes.map(node => ({
      id: node.path,
      type: 'default',
      position: { x: node.position[0], y: node.position[1] },
      data: node,
    })),
    [state.nodes]
  );

  const edges: RFEdge[] = useMemo(() =>
    state.connections.map(conn => ({
      id: conn.id,
      source: conn.source_node_path,
      target: conn.target_node_path,
      sourceHandle: `out-${conn.source_output_index}`,
      targetHandle: `in-${conn.target_input_index}`,
    })),
    [state.connections]
  );

  const onConnect: OnConnect = useCallback((params) => {
    if (!params.source || !params.target || !params.sourceHandle || !params.targetHandle) return;
    
    createConnection({
      source_node_path: params.source,
      source_output_index: parseInt(params.sourceHandle.split('-')[1]),
      target_node_path: params.target,
      target_input_index: parseInt(params.targetHandle.split('-')[1]),
    });
  }, [createConnection]);

  const onNodeDragStop: OnNodeDrag = useCallback((_, node) => {
    updateNodePosition(node.id, [node.position.x, node.position.y]);
  }, [updateNodePosition]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    const position = { x: event.clientX - 250, y: event.clientY - 100 };
    createNode(type, [position.x, position.y]);
  }, [createNode]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onConnect={onConnect}
        onNodeClick={(_, node) => selectNode(node.id)}
        onNodeDragStop={onNodeDragStop}
        onDragOver={onDragOver}
        onDrop={onDrop}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
};