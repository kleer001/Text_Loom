// AboutDialog Component - Shows application information

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Link,
} from '@mui/material';

interface AboutDialogProps {
  open: boolean;
  onClose: () => void;
}

export const AboutDialog: React.FC<AboutDialogProps> = ({ open, onClose }) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>About TextLoom</DialogTitle>
      <DialogContent>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h4" sx={{ mb: 2 }}>
            TextLoom
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Version 0.1.0
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            A node-based text processing and generation tool for creating complex text workflows.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Created by kleer001
          </Typography>
          <Link
            href="https://github.com/kleer001/Text_Loom"
            target="_blank"
            rel="noopener noreferrer"
            variant="body2"
          >
            github.com/kleer001/Text_Loom
          </Link>
        </Box>
      </DialogContent>
      <DialogActions sx={{ justifyContent: 'center', pb: 2 }}>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};
