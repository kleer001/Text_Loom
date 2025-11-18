// MenuBar Component - Classic desktop-style menu bar with File, Edit, Preferences, Help

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  ListItemText,
  Divider,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { useFileManager } from './hooks/useFileManager';
import { useWorkspace } from './WorkspaceContext';
import { useTheme } from './ThemeContext';
import { apiClient } from './apiClient';

// Props for dialogs that will be managed by parent
export interface MenuBarProps {
  onKeyboardShortcuts: () => void;
  onAbout: () => void;
}

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

export const MenuBar: React.FC<MenuBarProps> = ({ onKeyboardShortcuts, onAbout }) => {
  const { mode, toggleTheme } = useTheme();
  const { loadWorkspace } = useWorkspace();
  const { currentFilePath, isDirty, save, saveAs, open, newWorkspace } = useFileManager();

  // Menu anchor states
  const [fileAnchor, setFileAnchor] = useState<null | HTMLElement>(null);
  const [editAnchor, setEditAnchor] = useState<null | HTMLElement>(null);
  const [prefsAnchor, setPrefsAnchor] = useState<null | HTMLElement>(null);
  const [helpAnchor, setHelpAnchor] = useState<null | HTMLElement>(null);

  // Undo/redo state
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [undoDescription, setUndoDescription] = useState('');
  const [redoDescription, setRedoDescription] = useState('');

  // Autosave toggle state (persisted in localStorage)
  const [autosaveEnabled, setAutosaveEnabled] = useState(() => {
    const stored = localStorage.getItem('textloom-autosave');
    return stored !== 'false'; // default to true
  });

  // Confirm dialog state
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

  // Fetch undo/redo status
  const fetchUndoStatus = useCallback(async () => {
    try {
      const status = await apiClient.getUndoStatus();
      setCanUndo(status.can_undo);
      setCanRedo(status.can_redo);
      setUndoDescription(status.undo_description);
      setRedoDescription(status.redo_description);
    } catch (err) {
      console.error('Failed to fetch undo status:', err);
    }
  }, []);

  // Fetch undo status on mount and periodically
  useEffect(() => {
    fetchUndoStatus();
    const interval = setInterval(fetchUndoStatus, 2000);
    return () => clearInterval(interval);
  }, [fetchUndoStatus]);

  // Menu handlers
  const handleFileOpen = (event: React.MouseEvent<HTMLElement>) => {
    setFileAnchor(event.currentTarget);
  };

  const handleEditOpen = (event: React.MouseEvent<HTMLElement>) => {
    setEditAnchor(event.currentTarget);
  };

  const handlePrefsOpen = (event: React.MouseEvent<HTMLElement>) => {
    setPrefsAnchor(event.currentTarget);
  };

  const handleHelpOpen = (event: React.MouseEvent<HTMLElement>) => {
    setHelpAnchor(event.currentTarget);
  };

  const closeAllMenus = () => {
    setFileAnchor(null);
    setEditAnchor(null);
    setPrefsAnchor(null);
    setHelpAnchor(null);
  };

  // File menu actions
  const handleNewWorkspace = () => {
    closeAllMenus();
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

  const handleOpenFile = () => {
    closeAllMenus();
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
    closeAllMenus();
    save();
  };

  const handleSaveAs = () => {
    closeAllMenus();
    saveAs();
  };

  // Edit menu actions
  const handleUndo = async () => {
    closeAllMenus();
    try {
      await apiClient.undo();
      await loadWorkspace();
      fetchUndoStatus();
    } catch (err) {
      console.error('Undo failed:', err);
    }
  };

  const handleRedo = async () => {
    closeAllMenus();
    try {
      await apiClient.redo();
      await loadWorkspace();
      fetchUndoStatus();
    } catch (err) {
      console.error('Redo failed:', err);
    }
  };

  const handleCut = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:cut'));
  };

  const handleCopy = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:copy'));
  };

  const handlePaste = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:paste'));
  };

  const handleDuplicate = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:duplicate'));
  };

  const handleDelete = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:deleteSelected'));
  };

  const handleSelectAll = () => {
    closeAllMenus();
    window.dispatchEvent(new CustomEvent('textloom:selectAll'));
  };

  // Preferences actions
  const handleThemeToggle = () => {
    toggleTheme();
    // Don't close menu - let user see the change
  };

  const handleAutosaveToggle = () => {
    const newValue = !autosaveEnabled;
    setAutosaveEnabled(newValue);
    localStorage.setItem('textloom-autosave', String(newValue));
    // Note: The actual autosave behavior would need to be updated in useFileManager
    // to check this localStorage value. For now, we just store the preference.
  };

  // Help actions
  const handleKeyboardShortcuts = () => {
    closeAllMenus();
    onKeyboardShortcuts();
  };

  const handleDocumentation = () => {
    closeAllMenus();
    window.open('https://github.com/kleer001/Text_Loom', '_blank');
  };

  const handleReportIssue = () => {
    closeAllMenus();
    window.open('https://github.com/kleer001/Text_Loom/issues', '_blank');
  };

  const handleAbout = () => {
    closeAllMenus();
    onAbout();
  };

  // Confirm dialog handlers
  const handleConfirmDialogCancel = () => {
    setConfirmDialog({ open: false, title: '', message: '', action: null });
  };

  const handleConfirmDialogConfirm = () => {
    if (confirmDialog.action) {
      confirmDialog.action();
    }
  };

  // Menu button style for classic look
  const menuButtonSx = {
    color: 'inherit',
    textTransform: 'none' as const,
    minWidth: 'auto',
    px: 1.5,
    py: 0.5,
    fontSize: '0.875rem',
    '&:hover': {
      backgroundColor: 'action.hover',
    },
  };

  return (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0 }}>
        {/* File Menu */}
        <Button
          onClick={handleFileOpen}
          sx={menuButtonSx}
        >
          File
        </Button>
        <Menu
          anchorEl={fileAnchor}
          open={Boolean(fileAnchor)}
          onClose={closeAllMenus}
          MenuListProps={{ dense: true }}
        >
          <MenuItem onClick={handleNewWorkspace}>
            <ListItemText>New</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+N
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleOpenFile}>
            <ListItemText>Open...</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+O
            </Typography>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleSave}>
            <ListItemText>Save</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+S
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleSaveAs}>
            <ListItemText>Save As...</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+Shift+S
            </Typography>
          </MenuItem>
        </Menu>

        {/* Edit Menu */}
        <Button
          onClick={handleEditOpen}
          sx={menuButtonSx}
        >
          Edit
        </Button>
        <Menu
          anchorEl={editAnchor}
          open={Boolean(editAnchor)}
          onClose={closeAllMenus}
          MenuListProps={{ dense: true }}
        >
          <MenuItem onClick={handleUndo} disabled={!canUndo}>
            <ListItemText>
              Undo{undoDescription ? ` ${undoDescription}` : ''}
            </ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+Z
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleRedo} disabled={!canRedo}>
            <ListItemText>
              Redo{redoDescription ? ` ${redoDescription}` : ''}
            </ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+Shift+Z
            </Typography>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleCut}>
            <ListItemText>Cut</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+X
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleCopy}>
            <ListItemText>Copy</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+C
            </Typography>
          </MenuItem>
          <MenuItem onClick={handlePaste}>
            <ListItemText>Paste</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+V
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleDuplicate}>
            <ListItemText>Duplicate</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+D
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleDelete}>
            <ListItemText>Delete</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Delete
            </Typography>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleSelectAll}>
            <ListItemText>Select All</ListItemText>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              Ctrl+A
            </Typography>
          </MenuItem>
        </Menu>

        {/* Preferences Menu */}
        <Button
          onClick={handlePrefsOpen}
          sx={menuButtonSx}
        >
          Preferences
        </Button>
        <Menu
          anchorEl={prefsAnchor}
          open={Boolean(prefsAnchor)}
          onClose={closeAllMenus}
          MenuListProps={{ dense: true }}
        >
          <MenuItem onClick={handleThemeToggle}>
            <FormControlLabel
              control={
                <Switch
                  checked={mode === 'dark'}
                  size="small"
                  sx={{ mr: 1 }}
                />
              }
              label="Dark Mode"
              sx={{ m: 0, width: '100%' }}
            />
          </MenuItem>
          <MenuItem onClick={handleAutosaveToggle}>
            <FormControlLabel
              control={
                <Switch
                  checked={autosaveEnabled}
                  size="small"
                  sx={{ mr: 1 }}
                />
              }
              label="Autosave"
              sx={{ m: 0, width: '100%' }}
            />
          </MenuItem>
        </Menu>

        {/* Help Menu */}
        <Button
          onClick={handleHelpOpen}
          sx={menuButtonSx}
        >
          Help
        </Button>
        <Menu
          anchorEl={helpAnchor}
          open={Boolean(helpAnchor)}
          onClose={closeAllMenus}
          MenuListProps={{ dense: true }}
        >
          <MenuItem onClick={handleKeyboardShortcuts}>
            <ListItemText>Keyboard Shortcuts</ListItemText>
          </MenuItem>
          <MenuItem onClick={handleDocumentation}>
            <ListItemText>Documentation</ListItemText>
          </MenuItem>
          <MenuItem onClick={handleReportIssue}>
            <ListItemText>Report Issue</ListItemText>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleAbout}>
            <ListItemText>About TextLoom</ListItemText>
          </MenuItem>
        </Menu>

        {/* File path display */}
        <Box sx={{ ml: 2, display: 'flex', alignItems: 'center' }}>
          {currentFilePath && (
            <Typography variant="body2" sx={{ color: 'inherit', opacity: 0.8 }}>
              {currentFilePath}
              {isDirty && ' *'}
            </Typography>
          )}
          {!currentFilePath && isDirty && (
            <Typography variant="body2" sx={{ color: 'inherit', fontStyle: 'italic', opacity: 0.8 }}>
              Untitled *
            </Typography>
          )}
        </Box>
      </Box>

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
