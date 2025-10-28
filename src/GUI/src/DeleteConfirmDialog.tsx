// Delete Confirmation Dialog - Confirms deletion of nodes

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';

interface DeleteConfirmDialogProps {
  open: boolean;
  nodeCount: number;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteConfirmDialog: React.FC<DeleteConfirmDialogProps> = ({
  open,
  nodeCount,
  onConfirm,
  onCancel,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onCancel}
      aria-labelledby="delete-dialog-title"
      aria-describedby="delete-dialog-description"
    >
      <DialogTitle id="delete-dialog-title">
        Delete {nodeCount} {nodeCount === 1 ? 'Node' : 'Nodes'}?
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="delete-dialog-description">
          {nodeCount === 1
            ? 'Are you sure you want to delete this node? This action cannot be undone.'
            : `Are you sure you want to delete ${nodeCount} nodes? This action cannot be undone.`}
        </DialogContentText>
        <DialogContentText sx={{ mt: 2, fontWeight: 'bold' }}>
          All connections to {nodeCount === 1 ? 'this node' : 'these nodes'} will also be removed.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel} color="primary">
          Cancel
        </Button>
        <Button onClick={onConfirm} color="error" variant="contained" autoFocus>
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
};
