// AutosaveRecoveryDialog Component - Prompts user to recover autosaved workspace

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';

interface AutosaveRecoveryDialogProps {
  open: boolean;
  timestamp: number;
  filePath: string | null;
  onRecover: () => void;
  onDiscard: () => void;
}

export const AutosaveRecoveryDialog: React.FC<AutosaveRecoveryDialogProps> = ({
  open,
  timestamp,
  filePath,
  onRecover,
  onDiscard,
}) => {
  const formatTimestamp = (ts: number): string => {
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - ts;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays === 1) {
      return 'yesterday';
    } else {
      return `${diffDays} days ago`;
    }
  };

  return (
    <Dialog open={open} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <WarningIcon color="warning" />
          <span>Recover Unsaved Work?</span>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography gutterBottom>
          An autosaved workspace was found from <strong>{formatTimestamp(timestamp)}</strong>.
        </Typography>
        {filePath && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            File: {filePath}
          </Typography>
        )}
        <Typography variant="body2" sx={{ mt: 2 }}>
          Would you like to recover this workspace?
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onDiscard} color="error">
          Discard
        </Button>
        <Button onClick={onRecover} color="primary" variant="contained" autoFocus>
          Recover
        </Button>
      </DialogActions>
    </Dialog>
  );
};
