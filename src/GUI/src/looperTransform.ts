import type { NodeResponse } from './types';

export interface LooperSystem {
  looperNode: NodeResponse;
  inputNullNode: NodeResponse;
  outputNullNode: NodeResponse;
}

export interface TransformedNodes {
  displayNodes: NodeResponse[];
  looperSystems: Map<string, LooperSystem>;
}

const NODE_WIDTH = 250;

export function identifyLooperSystems(nodes: NodeResponse[]): Map<string, LooperSystem> {
  const looperSystems = new Map<string, LooperSystem>();
  const looperNodes = nodes.filter(n => n.type === 'looper');

  for (const looper of looperNodes) {
    const looperPath = looper.path;
    const inputNull = nodes.find(n =>
      n.type === 'input_null' &&
      n.path.startsWith(`${looperPath}/`) &&
      n.name === 'inputNullNode'
    );
    const outputNull = nodes.find(n =>
      n.type === 'output_null' &&
      n.path.startsWith(`${looperPath}/`) &&
      n.name === 'outputNullNode'
    );

    if (inputNull && outputNull) {
      looperSystems.set(looper.session_id, {
        looperNode: looper,
        inputNullNode: inputNull,
        outputNullNode: outputNull,
      });
    }
  }

  return looperSystems;
}

export function transformLooperNodes(nodes: NodeResponse[]): TransformedNodes {
  const looperSystems = identifyLooperSystems(nodes);
  const internalNodeIds = new Set<string>();

  for (const system of looperSystems.values()) {
    internalNodeIds.add(system.inputNullNode.session_id);
    internalNodeIds.add(system.outputNullNode.session_id);
  }

  const displayNodes: NodeResponse[] = [];

  for (const node of nodes) {
    if (internalNodeIds.has(node.session_id)) {
      continue;
    }

    if (node.type === 'looper') {
      const system = looperSystems.get(node.session_id);
      if (system) {
        displayNodes.push(createLooperStartNode(system));
        displayNodes.push(createLooperEndNode(system));
      }
    } else {
      displayNodes.push(node);
    }
  }

  return { displayNodes, looperSystems };
}

function createLooperStartNode(system: LooperSystem): NodeResponse {
  const { looperNode, inputNullNode } = system;

  return {
    ...looperNode,
    session_id: `${looperNode.session_id}_start`,
    name: `${looperNode.name}_start`,
    glyph: '⟲▷',
    type: 'looper_start',
    inputs: looperNode.inputs,
    outputs: inputNullNode.outputs,
  };
}

function createLooperEndNode(system: LooperSystem): NodeResponse {
  const { looperNode, outputNullNode } = system;
  const [x, y] = looperNode.position;

  return {
    ...outputNullNode,
    session_id: `${looperNode.session_id}_end`,
    name: `${looperNode.name}_end`,
    glyph: '◁',
    type: 'looper_end',
    position: [x + (NODE_WIDTH * 2), y],
  };
}

export function getOriginalNodeId(transformedId: string): string {
  return transformedId.replace(/_start$|_end$/, '');
}

export function isLooperPart(nodeType: string): boolean {
  return nodeType === 'looper_start' || nodeType === 'looper_end';
}
