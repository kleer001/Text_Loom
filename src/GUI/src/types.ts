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
  group: string;
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
  connection_id: string;
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
  name?: string;
  parameters?: Record<string, string | number | boolean | string[]>;
  position?: [number, number];
  color?: [number, number, number];
}

// Request types for connection operations
export interface ConnectionRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}

export interface ConnectionDeleteRequest {
  source_node_path: string;
  source_output_index: number;
  target_node_path: string;
  target_input_index: number;
}

// Execution types
export interface ExecutionResponse {
  success: boolean;
  message: string;
  output_data: string[][] | null;
  execution_time: number;
  node_state: string;
  errors: string[];
  warnings: string[];
}

// Global variables types
export interface GlobalResponse {
  key: string;
  value: string | number | boolean;
}

export interface GlobalsListResponse {
  globals: Record<string, string | number | boolean>;
}

export interface GlobalSetRequest {
  value: string | number | boolean;
}