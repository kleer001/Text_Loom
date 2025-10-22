import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Card, CardHeader, CardContent, Chip, Box, Typography } from '@mui/material';
import { NodeFlowData } from '../../../types/workspace';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

const getStateIcon = (state: string) => {
  switch (state) {
    case 'unchanged': return <CheckCircleIcon fontSize="small" color="success" />;
    case 'cooking': return <HourglassEmptyIcon fontSize="small" color="primary" />;
    case 'uncooked': return null;
    default: return null;
  }
};

const getStateColor = (state: string) => {
  switch (state) {
    case 'unchanged': return '#e8f5e9';
    case 'cooking': return '#e3f2fd';
    case 'uncooked': return '#f5f5f5';
    default: return '#fff';
  }
};

const CustomNode: React.FC<NodeProps<NodeFlowData>> = ({ data, selected }) => {
  const displayName = data.nodeType.replace(/_/g, ' ');
  const hasErrors = data.errors.length > 0;

  return (
    <Card
      sx={{
        minWidth: 180,
        border: selected ? '2px solid #1976d2' : '1px solid #ccc',
        backgroundColor: getStateColor(data.state),
        boxShadow: selected ? 4 : 1,
      }}
    >
      {/* Input Handles */}
      {data.inputSockets.map((socket) => (
        <Handle
          key={`in-${socket.index}`}
          type="target"
          position={Position.Left}
          id={`in-${socket.index}`}
          style={{ top: `${((socket.index + 1) * 100) / (data.inputSockets.length + 1)}%` }}
        />
      ))}

      {/* Output Handles */}
      {data.outputSockets.map((socket) => (
        <Handle
          key={`out-${socket.index}`}
          type="source"
          position={Position.Right}
          id={`out-${socket.index}`}
          style={{ top: `${((socket.index + 1) * 100) / (data.outputSockets.length + 1)}%` }}
        />
      ))}

      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="subtitle2" noWrap>
              {data.label}
            </Typography>
            {hasErrors && <ErrorIcon fontSize="small" color="error" />}
            {getStateIcon(data.state)}
          </Box>
        }
        subheader={
          <Typography variant="caption" color="textSecondary">
            {displayName}
          </Typography>
        }
        sx={{ py: 1, px: 1.5 }}
      />

      <CardContent sx={{ py: 1, px: 1.5, '&:last-child': { pb: 1 } }}>
        <Box display="flex" gap={0.5} flexWrap="wrap">
          {Object.keys(data.parameters).length > 0 && (
            <Chip label={`${Object.keys(data.parameters).length} params`} size="small" />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CustomNode;