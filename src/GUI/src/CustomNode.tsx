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
      {node.inputs.map((input) => (
        <Handle
          key={`input-${input.index}`}
          type="target"
          position={Position.Left}
          id={`input-${input.index}`}
          style={{
            background: input.connected ? '#4caf50' : '#757575',
            width: '10px',
            height: '10px',
          }}
        />
      ))}

      {/* Node content */}
      <div style={{ marginBottom: '4px' }}>
        <div style={{ 
          fontWeight: 'bold', 
          fontSize: '14px',
          marginBottom: '2px',
        }}>
          {node.name}
        </div>
        <div style={{ 
          fontSize: '11px', 
          color: '#666',
          marginBottom: '4px',
        }}>
          {node.type}
        </div>
        <div style={{ 
          fontSize: '10px', 
          color: '#999',
        }}>
          {node.path}
        </div>
      </div>

      {/* State indicator */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          marginTop: '6px',
        }}
      >
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: stateColor,
          }}
        />
        <span style={{ color: '#666' }}>{node.state}</span>
      </div>

      {/* Output handles */}
      {node.outputs.map((output) => (
        <Handle
          key={`output-${output.index}`}
          type="source"
          position={Position.Right}
          id={`output-${output.index}`}
          style={{
            background: output.connection_count > 0 ? '#4caf50' : '#757575',
            width: '10px',
            height: '10px',
          }}
        />
      ))}
    </div>
  );
};