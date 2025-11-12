import type { ConnectionResponse, NodeResponse, InputInfo, OutputInfo } from '../types';
import type { LooperSystem } from '../looperTransform';

export function transformConnectionNodeIds(
  connections: ConnectionResponse[],
  looperSystems: Map<string, LooperSystem>
): ConnectionResponse[] {
  return connections.map(conn => {
    let sourceId = conn.source_node_session_id;
    let targetId = conn.target_node_session_id;

    for (const system of looperSystems.values()) {
      if (conn.source_node_session_id === system.inputNullNode.session_id) {
        sourceId = `${system.looperNode.session_id}_start`;
      }
      if (conn.source_node_session_id === system.outputNullNode.session_id) {
        sourceId = `${system.looperNode.session_id}_end`;
      }
      if (conn.target_node_session_id === system.inputNullNode.session_id) {
        targetId = `${system.looperNode.session_id}_start`;
      }
      if (conn.target_node_session_id === system.outputNullNode.session_id) {
        targetId = `${system.looperNode.session_id}_end`;
      }
    }

    return { ...conn, source_node_session_id: sourceId, target_node_session_id: targetId };
  });
}

function countOutputConnections(
  nodeId: string,
  outputIndex: number | string,
  connections: ConnectionResponse[]
): number {
  return connections.filter(
    conn => conn.source_node_session_id === nodeId && conn.source_output_index === outputIndex
  ).length;
}

function hasInputConnection(
  nodeId: string,
  inputIndex: number | string,
  connections: ConnectionResponse[]
): boolean {
  return connections.some(
    conn => conn.target_node_session_id === nodeId && conn.target_input_index === inputIndex
  );
}

function updateOutputConnectionCounts(
  outputs: OutputInfo[],
  nodeId: string,
  connections: ConnectionResponse[]
): OutputInfo[] {
  return outputs.map(output => ({
    ...output,
    connection_count: countOutputConnections(nodeId, output.index, connections),
  }));
}

function updateInputConnectedFlags(
  inputs: InputInfo[],
  nodeId: string,
  connections: ConnectionResponse[]
): InputInfo[] {
  return inputs.map(input => ({
    ...input,
    connected: hasInputConnection(nodeId, input.index, connections),
  }));
}

export function enrichNodesWithConnectionState(
  nodes: NodeResponse[],
  connections: ConnectionResponse[]
): NodeResponse[] {
  return nodes.map(node => ({
    ...node,
    outputs: updateOutputConnectionCounts(node.outputs, node.session_id, connections),
    inputs: updateInputConnectedFlags(node.inputs, node.session_id, connections),
  }));
}
