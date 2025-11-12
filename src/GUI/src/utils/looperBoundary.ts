import type { Node } from '@xyflow/react';
import type { NodeResponse } from '../types';
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

function mapToDisplayNodes(childNodes: NodeResponse[], displayNodes: Node[]): Node[] {
  return childNodes
    .map(childNode => displayNodes.find(n => n.id === childNode.session_id))
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
  displayNodes: Node[]
): Node[] {
  const childNodes = findChildNodesInLooper(workspaceNodes, system);
  const displayChildNodes = mapToDisplayNodes(childNodes, displayNodes);
  const looperDisplayNodes = findLooperDisplayNodes(displayNodes, system.looperNode.session_id);

  return [...looperDisplayNodes, ...displayChildNodes];
}
