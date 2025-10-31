// Edge Mapping - Convert backend ConnectionResponse to React Flow Edge format

import type { Edge } from '@xyflow/react';
import type { ConnectionResponse } from '../types';

/**
 * Convert ConnectionResponse from backend to React Flow Edge format
 *
 * Creates a unique edge ID using all 4 identifying components:
 * {source_node_session_id}-{source_output_index}-{target_node_session_id}-{target_input_index}
 *
 * Maps backend indices to React Flow handle IDs:
 * - source_output_index: 0 → sourceHandle: "output-0"
 * - target_input_index: 0 → targetHandle: "input-0"
 */
export function connectionToEdge(connection: ConnectionResponse): Edge {
  return {
    id: `${connection.source_node_session_id}-${connection.source_output_index}-${connection.target_node_session_id}-${connection.target_input_index}`,
    source: connection.source_node_session_id,
    target: connection.target_node_session_id,
    sourceHandle: `output-${connection.source_output_index}`,
    targetHandle: `input-${connection.target_input_index}`,
  };
}

/**
 * Convert array of ConnectionResponse to Edge[]
 *
 * Optionally applies styling and edge type options
 */
export function connectionsToEdges(
  connections: ConnectionResponse[],
  options?: {
    type?: 'default' | 'smoothstep' | 'step' | 'straight';
    animated?: boolean;
    style?: React.CSSProperties;
  }
): Edge[] {
  return connections.map(conn => ({
    ...connectionToEdge(conn),
    ...options,
  }));
}
