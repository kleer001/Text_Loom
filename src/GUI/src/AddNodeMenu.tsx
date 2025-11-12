// Add Node Menu - Allows users to create new nodes

import React, { useState, useEffect } from 'react';
import {
  Button,
  CircularProgress,
  Fab,
  Tooltip,
  Popover,
  Box,
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

/**
 * Calculate grid dimensions for a square layout
 * Returns number of columns based on item count
 */
const calculateGridColumns = (itemCount: number): number => {
  return Math.ceil(Math.sqrt(itemCount));
};

/**
 * Node Type Button - Individual node type selector
 */
interface NodeTypeButtonProps {
  nodeType: NodeTypeInfo;
  onClick: () => void;
  disabled: boolean;
}

const NodeTypeButton: React.FC<NodeTypeButtonProps> = ({
  nodeType,
  onClick,
  disabled,
}) => (
  <Box
    onClick={disabled ? undefined : onClick}
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 2,
      backgroundColor: '#f5f5f5',
      border: '1px solid #e0e0e0',
      borderRadius: 1,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.5 : 1,
      transition: 'all 0.2s ease',
      '&:hover': disabled
        ? {}
        : {
            backgroundColor: '#e8e8e8',
            transform: 'translateY(-2px)',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          },
    }}
  >
    <Box
      sx={{
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: 0.5,
      }}
    >
      {nodeType.glyph}
    </Box>
    <Box
      sx={{
        fontSize: '12px',
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      {nodeType.label}
    </Box>
  </Box>
);

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
    const startX = 100;
    const startY = 100;
    const gridSpacing = 250;

    const nodeCount = nodes.length;
    const col = nodeCount % 4;
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
  const gridColumns = calculateGridColumns(nodeTypes.length);

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

      <Popover
        anchorEl={anchorEl}
        open={isOpen}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ p: 2 }}>
          {loading ? (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                padding: 2,
              }}
            >
              <CircularProgress size={20} />
              <Box>Loading...</Box>
            </Box>
          ) : (
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: `repeat(${gridColumns}, 1fr)`,
                gap: 1.5,
                minWidth: 'fit-content',
              }}
            >
              {nodeTypes.map((nodeType) => (
                <NodeTypeButton
                  key={nodeType.id}
                  nodeType={nodeType}
                  onClick={() => handleCreateNode(nodeType.id)}
                  disabled={creating}
                />
              ))}
            </Box>
          )}
        </Box>
      </Popover>
    </>
  );
};
