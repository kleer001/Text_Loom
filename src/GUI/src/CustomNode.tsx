import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeResponse } from './types';

interface CustomNodeData {
  node: NodeResponse;
}

const MIN_HANDLE_SPACING = 12;
const VERTICAL_PADDING = 20;

const STATE_COLORS: Record<string, string> = {
  unchanged: '#4caf50',
  uncooked: '#ff9800',
  cooking: '#2196f3',
};

function calculateMinHeight(inputCount: number, outputCount: number): number {
  const handleCount = Math.max(inputCount, outputCount);
  return handleCount > 0 ? (handleCount + 1) * MIN_HANDLE_SPACING + VERTICAL_PADDING : 0;
}

export const CustomNode: React.FC<{ data: CustomNodeData; selected?: boolean }> = ({ data, selected }) => {
  const { node } = data;

  const minHeight = calculateMinHeight(node.inputs.length, node.outputs.length);
  const stateColor = STATE_COLORS[node.state] ?? '#757575';
  const borderColor = selected ? '#1976d2' : '#ccc';

  return (
    <div
      style={{
        padding: '10px 15px',
        border: `2px solid ${borderColor}`,
        borderRadius: '8px',
        background: 'white',
        minWidth: '150px',
        minHeight: minHeight || undefined,
        boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
      }}
    >
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

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
          }}
        >
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: stateColor,
              flexShrink: 0,
            }}
          />

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