import type { Node } from '@xyflow/react';
import type { NodeResponse, ConnectionResponse } from '../types';
import type { LooperSystem } from '../looperTransform';

function isLooperInternalNode(nodeId: string, system: LooperSystem): boolean {
  return (
    nodeId === system.inputNullNode.session_id ||
    nodeId === system.outputNullNode.session_id
  );
}

function findChildNodesInLooper(
  workspaceNodes: NodeResponse[],
  system: LooperSystem
): NodeResponse[] {
  const looperPath = system.looperNode.path;
  return workspaceNodes.filter(
    n => n.path.startsWith(`${looperPath}/`) && !isLooperInternalNode(n.session_id, system)
  );
}

function findNodesConnectedToLooperStart(
  connections: ConnectionResponse[],
  looperId: string
): string[] {
  const looperStartId = `${looperId}_start`;
  return connections
    .filter(conn => conn.source_node_session_id === looperStartId)
    .map(conn => conn.target_node_session_id);
}

function findNodesConnectedToLooperEnd(
  connections: ConnectionResponse[],
  looperId: string
): string[] {
  const looperEndId = `${looperId}_end`;
  return connections
    .filter(conn => conn.target_node_session_id === looperEndId)
    .map(conn => conn.source_node_session_id);
}

function findDisplayNodesByIds(displayNodes: Node[], nodeIds: string[]): Node[] {
  return nodeIds
    .map(id => displayNodes.find(n => n.id === id))
    .filter((n): n is Node => n !== undefined);
}

function findLooperDisplayNodes(displayNodes: Node[], looperId: string): Node[] {
  return displayNodes.filter(
    n => n.id === `${looperId}_start` || n.id === `${looperId}_end`
  );
}

export function gatherBoundaryNodes(
  system: LooperSystem,
  workspaceNodes: NodeResponse[],
  displayNodes: Node[],
  connections: ConnectionResponse[]
): Node[] {
  const looperId = system.looperNode.session_id;
  const childNodes = findChildNodesInLooper(workspaceNodes, system);
  const displayChildNodes = childNodes
    .map(childNode => displayNodes.find(n => n.id === childNode.session_id))
    .filter((n): n is Node => n !== undefined);

  const looperDisplayNodes = findLooperDisplayNodes(displayNodes, looperId);
  const connectedToStartIds = findNodesConnectedToLooperStart(connections, looperId);
  const connectedToEndIds = findNodesConnectedToLooperEnd(connections, looperId);
  const connectedToStart = findDisplayNodesByIds(displayNodes, connectedToStartIds);
  const connectedToEnd = findDisplayNodesByIds(displayNodes, connectedToEndIds);

  return [...looperDisplayNodes, ...displayChildNodes, ...connectedToStart, ...connectedToEnd];
}
