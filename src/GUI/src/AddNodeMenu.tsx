// Add Node Menu - Allows users to create new nodes

import React, { useState } from 'react';
import {
  Button,
  Menu,
  MenuItem,
  ListItemText,
  CircularProgress,
  Fab,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useWorkspace } from './WorkspaceContext';

// Available node types from the backend
const NODE_TYPES = [
  { id: 'text', label: 'Text', description: 'Text content node' },
  { id: 'file_in', label: 'File In', description: 'Read file input' },
  { id: 'file_out', label: 'File Out', description: 'Write file output' },
  { id: 'folder', label: 'Folder', description: 'Directory operations' },
  { id: 'json', label: 'JSON', description: 'JSON processing' },
  { id: 'looper', label: 'Looper', description: 'Loop over items' },
  { id: 'make_list', label: 'Make List', description: 'Create list' },
  { id: 'merge', label: 'Merge', description: 'Merge inputs' },
  { id: 'null', label: 'Null', description: 'Null node' },
  { id: 'query', label: 'Query', description: 'Query operations' },
  { id: 'section', label: 'Section', description: 'Section node' },
  { id: 'split', label: 'Split', description: 'Split text' },
  { id: 'input_null', label: 'Input Null', description: 'Null input' },
  { id: 'output_null', label: 'Output Null', description: 'Null output' },
];

interface AddNodeMenuProps {
  variant?: 'fab' | 'button';
  onNodeCreated?: () => void;
}

export const AddNodeMenu: React.FC<AddNodeMenuProps> = ({
  variant = 'fab',
  onNodeCreated,
}) => {
  const { createNode, nodes } = useWorkspace();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [creating, setCreating] = useState(false);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const calculateNodePosition = (): [number, number] => {
    // Auto-position: place new nodes in a grid pattern
    // Starting position
    const startX = 100;
    const startY = 100;
    const gridSpacing = 250;

    // Calculate position based on node count
    const nodeCount = nodes.length;
    const col = nodeCount % 4; // 4 columns
    const row = Math.floor(nodeCount / 4);

    return [startX + col * gridSpacing, startY + row * gridSpacing];
  };

  const handleCreateNode = async (nodeType: string) => {
    setCreating(true);
    handleClose();

    try {
      const position = calculateNodePosition();
      await createNode({
        type: nodeType,
        position,
      });
      onNodeCreated?.();
    } catch (error) {
      console.error('Failed to create node:', error);
    } finally {
      setCreating(false);
    }
  };

  const isOpen = Boolean(anchorEl);

  return (
    <>
      {variant === 'fab' ? (
        <Tooltip title="Add Node" placement="left">
          <Fab
            color="primary"
            aria-label="add node"
            onClick={handleClick}
            disabled={creating}
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000,
            }}
          >
            {creating ? <CircularProgress size={24} color="inherit" /> : <AddIcon />}
          </Fab>
        </Tooltip>
      ) : (
        <Button
          variant="contained"
          startIcon={creating ? <CircularProgress size={20} /> : <AddIcon />}
          onClick={handleClick}
          disabled={creating}
        >
          Add Node
        </Button>
      )}

      <Menu
        anchorEl={anchorEl}
        open={isOpen}
        onClose={handleClose}
        PaperProps={{
          style: {
            maxHeight: 400,
            width: '280px',
          },
        }}
      >
        {NODE_TYPES.map((nodeType) => (
          <MenuItem
            key={nodeType.id}
            onClick={() => handleCreateNode(nodeType.id)}
            disabled={creating}
          >
            <ListItemText
              primary={nodeType.label}
              secondary={nodeType.description}
              secondaryTypographyProps={{
                variant: 'caption',
                color: 'text.secondary',
              }}
            />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};
