// FileMenu Component - File operations menu

import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
  Box,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import SaveIcon from '@mui/icons-material/Save';
import SaveAsIcon from '@mui/icons-material/SaveAs';
import DescriptionIcon from '@mui/icons-material/Description';
import { useFileManager } from './hooks/useFileManager';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({ open, title, message, onConfirm, onCancel }) => {
  return (
    <Dialog open={open} onClose={onCancel}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Typography>{message}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button onClick={onConfirm} color="primary" variant="contained">
          Confirm
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export const FileMenu: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    message: string;
    action: (() => void) | null;
  }>({
    open: false,
    title: '',
    message: '',
    action: null,
  });

  const { currentFilePath, isDirty, save, saveAs, open, newWorkspace } = useFileManager();

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNewWorkspace = () => {
    handleMenuClose();

    if (isDirty) {
      setConfirmDialog({
        open: true,
        title: 'Unsaved Changes',
        message: 'You have unsaved changes. Creating a new workspace will discard them. Continue?',
        action: () => {
          newWorkspace();
          setConfirmDialog({ open: false, title: '', message: '', action: null });
        },
      });
    } else {
      newWorkspace();
    }
  };

  const handleOpen = () => {
    handleMenuClose();

    if (isDirty) {
      setConfirmDialog({
        open: true,
        title: 'Unsaved Changes',
        message: 'You have unsaved changes. Opening a file will discard them. Continue?',
        action: () => {
          open();
          setConfirmDialog({ open: false, title: '', message: '', action: null });
        },
      });
    } else {
      open();
    }
  };

  const handleSave = () => {
    handleMenuClose();
    save();
  };

  const handleSaveAs = () => {
    handleMenuClose();
    saveAs();
  };

  const handleConfirmDialogCancel = () => {
    setConfirmDialog({ open: false, title: '', message: '', action: null });
  };

  const handleConfirmDialogConfirm = () => {
    if (confirmDialog.action) {
      confirmDialog.action();
    }
  };

  const menuOpen = Boolean(anchorEl);

  return (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title="File menu">
          <IconButton
            onClick={handleMenuOpen}
            size="small"
            sx={{ color: 'inherit' }}
          >
            <MenuIcon />
          </IconButton>
        </Tooltip>

        {currentFilePath && (
          <Typography variant="body2" sx={{ color: 'inherit' }}>
            {currentFilePath}
            {isDirty && ' *'}
          </Typography>
        )}

        {!currentFilePath && isDirty && (
          <Typography variant="body2" sx={{ color: 'inherit', fontStyle: 'italic' }}>
            Untitled *
          </Typography>
        )}
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleNewWorkspace}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>New Workspace</ListItemText>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Ctrl+N
          </Typography>
        </MenuItem>

        <MenuItem onClick={handleOpen}>
          <ListItemIcon>
            <FolderOpenIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Open...</ListItemText>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Ctrl+O
          </Typography>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleSave}>
          <ListItemIcon>
            <SaveIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Save</ListItemText>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Ctrl+S
          </Typography>
        </MenuItem>

        <MenuItem onClick={handleSaveAs}>
          <ListItemIcon>
            <SaveAsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Save As...</ListItemText>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Ctrl+Shift+S
          </Typography>
        </MenuItem>
      </Menu>

      <ConfirmDialog
        open={confirmDialog.open}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={handleConfirmDialogConfirm}
        onCancel={handleConfirmDialogCancel}
      />
    </>
  );
};
