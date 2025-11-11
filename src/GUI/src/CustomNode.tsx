// Custom Node Component - Displays node in React Flow graph

import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse } from './types';

interface CustomNodeData {
  node: NodeResponse;
}

export const CustomNode: React.FC<{ data: CustomNodeData; selected?: boolean }> = ({ data, selected }) => {
  const { node } = data;

  // State color mapping
  const getStateColor = (state: string): string => {
    switch (state) {
      case 'unchanged': return '#4caf50';
      case 'uncooked': return '#ff9800';
      case 'cooking': return '#2196f3';
      default: return '#757575';
    }
  };

  const stateColor = getStateColor(node.state);
  const borderColor = selected ? '#1976d2' : '#ccc';

  return (
    <div
      style={{
        padding: '10px 15px',
        border: `2px solid ${borderColor}`,
        borderRadius: '8px',
        background: 'white',
        minWidth: '150px',
        boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
      }}
    >
      {/* Input handles */}
      {node.inputs.map((input, idx) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${idx}`}
          title={`${input.name} (${input.data_type})`}
          style={{
            top: `${((idx + 1) / (node.inputs.length + 1)) * 100}%`,
            background: input.connected ? '#4caf50' : '#757575',
            width: '10px',
            height: '10px',
          }}
        />
      ))}

      {/* Node content */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {/* Top Row: Cook Circle | Node Glyph | Node Type */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
          }}
        >
          {/* Cooking color circle (left) */}
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: stateColor,
              flexShrink: 0,
            }}
          />

          {/* Node glyph (middle) */}
          <div
            style={{
              fontSize: '18px',
              fontWeight: 'bold',
              flex: 1,
              textAlign: 'center',
            }}
          >
            {node.glyph || '?'}
          </div>

          {/* Node type (right) */}
          <div
            style={{
              fontSize: '11px',
              color: '#666',
              fontWeight: '500',
              flexShrink: 0,
            }}
          >
            {node.type}
          </div>
        </div>

        {/* Bottom Row: Node Name (centered) */}
        <div
          style={{
            fontSize: '12px',
            fontWeight: 'bold',
            textAlign: 'center',
            color: '#333',
          }}
        >
          {node.name}
        </div>
      </div>

      {/* Output handles */}
      {node.outputs.map((output, idx) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${idx}`}
          title={`${output.name} (${output.data_type})`}
          style={{
            top: `${((idx + 1) / (node.outputs.length + 1)) * 100}%`,
            background: output.connection_count > 0 ? '#4caf50' : '#757575',
            width: '10px',
            height: '10px',
          }}
        />
      ))}
    </div>
  );
};