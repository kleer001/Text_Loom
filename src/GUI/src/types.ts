// API Response Types - Matches backend models exactly

export interface ParameterInfo {
  type: string;
  value: string | number | boolean | string[];
  default: string | number | boolean | string[];
  read_only: boolean;
}

export interface InputInfo {
  index: number | string;
  name: string;
  data_type: string;
  connected: boolean;
}

export interface OutputInfo {
  index: number | string;
  name: string;
  data_type: string;
  connection_count: number;
}

export interface NodeResponse {
  session_id: string;
  name: string;
  path: string;
  type: string;
  glyph: string;
  state: string;
  parameters: Record<string, ParameterInfo>;
  inputs: InputInfo[];
  outputs: OutputInfo[];
  errors: string[];
  warnings: string[];
  position: [number, number];
  color: [number, number, number];
  is_time_dependent: boolean;
  cook_count: number;
  last_cook_time: number;
}

export interface ConnectionResponse {
  source_node_session_id: string;
  source_node_path: string;
  source_output_index: number;
  source_output_name: string;
  target_node_session_id: string;
  target_node_path: string;
  target_input_index: number;
  target_input_name: string;
}

export interface WorkspaceState {
  nodes: NodeResponse[];
  connections: ConnectionResponse[];
  globals: Record<string, string | number | boolean>;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, string | number | boolean>;
}

// Request types for node operations
export interface NodeCreateRequest {
  type: string;
  name?: string;
  parent_path?: string;
  position?: [number, number];
}

export interface NodeUpdateRequest {
  parameters?: Record<string, string | number | boolean | string[]>;
  position?: [number, number];
  color?: [number, number, number];
}