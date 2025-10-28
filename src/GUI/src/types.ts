// Phase 1: Minimal types for displaying workspace

export interface NodeData {
  session_id: number;
  name: string;
  path: string;
  type: string;
  position: [number, number];
  inputs: Array<{
    index: number;
    name: string;
  }>;
  outputs: Array<{
    index: number;
    name: string;
  }>;
}

export interface ConnectionData {
  id: string;
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}

export interface WorkspaceResponse {
  nodes: NodeData[];
  connections: ConnectionData[];
  globals: Record<string, string>;
}