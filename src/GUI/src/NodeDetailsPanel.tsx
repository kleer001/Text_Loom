// Node Details Panel - Shows information about selected node

import React from 'react';
import { Box, Typography, Divider, Chip } from '@mui/material';
import type { NodeResponse } from './types';

interface NodeDetailsPanelProps {
  node: NodeResponse | null;
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node }) => {
  if (!node) {
    return (
      <Box sx={{ p: 2, color: 'text.secondary' }}>
        <Typography variant="body2">
          Select a node to view details
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, overflow: 'auto', height: '100%' }}>
      {/* Header */}
      <Typography variant="h6" gutterBottom>
        {node.name}
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        {node.type}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
        {node.path}
      </Typography>

      <Divider sx={{ my: 2 }} />

      {/* State */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          State
        </Typography>
        <Chip 
          label={node.state} 
          size="small" 
          color={node.state === 'unchanged' ? 'success' : 'warning'}
        />
        <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
          Cook count: {node.cook_count}
        </Typography>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Parameters */}
      <Typography variant="subtitle2" gutterBottom>
        Parameters
      </Typography>
      {Object.keys(node.parameters).length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No parameters
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {Object.entries(node.parameters).map(([name, param]) => (
            <Box key={name} sx={{ mb: 1.5 }}>
              <Typography variant="body2" fontWeight="bold">
                {name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {param.type} {param.read_only && '(read-only)'}
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  mt: 0.5, 
                  fontFamily: 'monospace',
                  bgcolor: 'grey.100',
                  p: 0.5,
                  borderRadius: 1,
                  fontSize: '12px',
                }}
              >
                {String(param.value)}
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Inputs */}
      <Typography variant="subtitle2" gutterBottom>
        Inputs
      </Typography>
      {node.inputs.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No inputs
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {node.inputs.map((input) => (
            <Box key={input.index} sx={{ mb: 1 }}>
              <Typography variant="body2">
                [{input.index}] {input.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {input.data_type} • {input.connected ? 'Connected' : 'Not connected'}
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Outputs */}
      <Typography variant="subtitle2" gutterBottom>
        Outputs
      </Typography>
      {node.outputs.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No outputs
        </Typography>
      ) : (
        <Box sx={{ mb: 2 }}>
          {node.outputs.map((output) => (
            <Box key={output.index} sx={{ mb: 1 }}>
              <Typography variant="body2">
                [{output.index}] {output.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {output.data_type} • {output.connection_count} connection(s)
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      {/* Errors */}
      {node.errors.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" color="error" gutterBottom>
            Errors
          </Typography>
          {node.errors.map((error, idx) => (
            <Typography key={idx} variant="body2" color="error" sx={{ mb: 0.5 }}>
              • {error}
            </Typography>
          ))}
        </>
      )}

      {/* Warnings */}
      {node.warnings.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" color="warning.main" gutterBottom>
            Warnings
          </Typography>
          {node.warnings.map((warning, idx) => (
            <Typography key={idx} variant="body2" color="warning.main" sx={{ mb: 0.5 }}>
              • {warning}
            </Typography>
          ))}
        </>
      )}
    </Box>
  );
};
