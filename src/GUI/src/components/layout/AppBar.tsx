// src/GUI/components/layout/AppBar.tsx

import { AppBar as MuiAppBar, Toolbar, Typography, IconButton, Box, Chip } from '@mui/material';
import { Refresh, Error as ErrorIcon } from '@mui/icons-material';
import { useWorkspace } from '../../contexts/WorkspaceContext';

export const AppBar = () => {
  const { state, fetchWorkspace } = useWorkspace();

  return (
    <MuiAppBar position="static" elevation={1}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          TextLoom
        </Typography>

        <Box display="flex" alignItems="center" gap={2}>
          {state.error && (
            <Chip 
              icon={<ErrorIcon />} 
              label="Error" 
              color="error" 
              size="small" 
            />
          )}
          
          {state.loading && (
            <Chip label="Loading..." size="small" />
          )}

          <IconButton 
            color="inherit" 
            onClick={fetchWorkspace}
            disabled={state.loading}
          >
            <Refresh />
          </IconButton>
        </Box>
      </Toolbar>
    </MuiAppBar>
  );
};