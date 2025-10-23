// src/GUI/src/types/workspace.ts



export interface Parameter {
  type: 'STRING' | 'INT' | 'FLOAT' | 'TOGGLE' | 'BUTTON' | 'STRINGLIST';
  value: unknown;  // Better than 'any' for values that could be anything
  default: unknown;
  read_only: boolean;
}

export interface Socket {
  index: number;
  name: string;
  data_type: string;
  connected: boolean;
}

export interface NodeData {
  session_id: number;
  name: string;
  path: string;
  type: string;
  state: 'unchanged' | 'uncooked' | 'cooking';
  parameters: Record<string, Parameter>;
  inputs: Socket[];
  outputs: Socket[];
  errors: string[];
  warnings: string[];
  position: [number, number];
  // Removed: selected - handled by ReactFlow
  output_data?: unknown[];  // Renamed and better typed than any[]
}

export interface ConnectionData {
  id: string;
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}

export interface WorkspaceState {
  nodes: NodeData[];
  connections: ConnectionData[];
  loading: boolean;
  error: string | null;
  lastUpdate: number;
}

export interface WorkspaceResponse {
  nodes: NodeData[];
  connections: ConnectionData[];
  globals: Record<string, string>;
}

export type WorkspaceAction =
  | { type: 'SET_WORKSPACE'; payload: { nodes: NodeData[]; connections: ConnectionData[] } }
  | { type: 'UPDATE_NODE'; payload: NodeData }
  | { type: 'DELETE_NODE'; payload: string }
  | { type: 'ADD_CONNECTION'; payload: ConnectionData }
  | { type: 'DELETE_CONNECTION'; payload: string }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };