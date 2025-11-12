// Add Node Menu - Allows users to create new nodes

import React, { useState, useEffect } from 'react';
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
import { apiClient } from './apiClient';

interface NodeTypeInfo {
  id: string;
  label: string;
  glyph: string;
}

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
  const [nodeTypes, setNodeTypes] = useState<NodeTypeInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNodeTypes = async () => {
      try {
        const types = await apiClient.getNodeTypes();
        setNodeTypes(types);
      } catch (error) {
        console.error('Failed to fetch node types:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNodeTypes();
  }, []);

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
        {loading ? (
          <MenuItem disabled>
            <CircularProgress size={20} />
            <ListItemText primary="Loading..." sx={{ ml: 2 }} />
          </MenuItem>
        ) : (
          nodeTypes.map((nodeType) => (
            <MenuItem
              key={nodeType.id}
              onClick={() => handleCreateNode(nodeType.id)}
              disabled={creating}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
              }}
            >
              <span style={{ fontSize: '18px', fontWeight: 'bold', minWidth: '24px' }}>
                {nodeType.glyph}
              </span>
              <ListItemText
                primary={nodeType.label}
              />
            </MenuItem>
          ))
        )}
      </Menu>
    </>
  );
};
