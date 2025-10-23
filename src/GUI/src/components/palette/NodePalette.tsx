// src/GUI/src/components/palette/NodePalette.tsx

import React, { useState, useEffect } from 'react';
import { Box, Fab, Drawer, List, ListItem, ListItemButton, ListItemText, Typography, CircularProgress } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useWorkspace } from '../../contexts/WorkspaceContext';
import { fetchAvailableNodeTypes } from '../../api/endpoints';

export const NodePalette: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [nodeTypes, setNodeTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const { createNode } = useWorkspace();

  useEffect(() => {
    const loadNodeTypes = async () => {
      setLoading(true);
      try {
        const types = await fetchAvailableNodeTypes();
        setNodeTypes(types);
      } catch (error) {
        console.error('Failed to load node types:', error);
      } finally {
        setLoading(false);
      }
    };

    if (open && nodeTypes.length === 0) {
      loadNodeTypes();
    }
  }, [open, nodeTypes.length]);

  const handleCreateNode = async (type: string) => {
    const x = Math.random() * 400;
    const y = Math.random() * 400;
    await createNode(type, [x, y]);
    setOpen(false);
  };

  return (
    <>
      <Fab
        color="primary"
        size="small"
        onClick={() => setOpen(true)}
        sx={{ position: 'absolute', top: 16, left: 16, zIndex: 1000 }}
      >
        <AddIcon />
      </Fab>
      <Drawer anchor="left" open={open} onClose={() => setOpen(false)}>
        <Box sx={{ width: 250, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Create Node
          </Typography>
          {loading ? (
            <Box display="flex" justifyContent="center" p={2}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {nodeTypes.map((type) => (
                <ListItem key={type} disablePadding>
                  <ListItemButton onClick={() => handleCreateNode(type)}>
                    <ListItemText primary={type.replace(/_/g, ' ')} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Drawer>
    </>
  );
};

export default NodePalette;