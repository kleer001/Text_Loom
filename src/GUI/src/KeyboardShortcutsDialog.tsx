// KeyboardShortcutsDialog Component - Shows all keyboard shortcuts

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider,
} from '@mui/material';

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onClose: () => void;
}

interface ShortcutItem {
  keys: string;
  description: string;
}

interface ShortcutSection {
  title: string;
  shortcuts: ShortcutItem[];
}

const shortcutSections: ShortcutSection[] = [
  {
    title: 'File',
    shortcuts: [
      { keys: 'Ctrl+N', description: 'New workspace' },
      { keys: 'Ctrl+O', description: 'Open workspace' },
      { keys: 'Ctrl+S', description: 'Save' },
      { keys: 'Ctrl+Shift+S', description: 'Save As' },
    ],
  },
  {
    title: 'Edit',
    shortcuts: [
      { keys: 'Ctrl+Z', description: 'Undo' },
      { keys: 'Ctrl+Shift+Z', description: 'Redo' },
      { keys: 'Ctrl+X', description: 'Cut' },
      { keys: 'Ctrl+C', description: 'Copy' },
      { keys: 'Ctrl+V', description: 'Paste' },
      { keys: 'Ctrl+D', description: 'Duplicate' },
      { keys: 'Delete', description: 'Delete selected' },
      { keys: 'Ctrl+A', description: 'Select all' },
    ],
  },
  {
    title: 'Canvas',
    shortcuts: [
      { keys: 'Scroll', description: 'Zoom in/out' },
      { keys: 'Click + Drag', description: 'Pan canvas' },
      { keys: 'Shift + Click', description: 'Multi-select nodes' },
    ],
  },
  {
    title: 'Nodes',
    shortcuts: [
      { keys: 'Double-click', description: 'Edit node name' },
      { keys: 'Click', description: 'Select node' },
      { keys: 'Drag', description: 'Move node' },
    ],
  },
];

export const KeyboardShortcutsDialog: React.FC<KeyboardShortcutsDialogProps> = ({
  open,
  onClose,
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Keyboard Shortcuts</DialogTitle>
      <DialogContent>
        {shortcutSections.map((section, sectionIndex) => (
          <Box key={section.title} sx={{ mb: sectionIndex < shortcutSections.length - 1 ? 2 : 0 }}>
            <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
              {section.title}
            </Typography>
            {section.shortcuts.map((shortcut) => (
              <Box
                key={shortcut.keys}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  py: 0.5,
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  {shortcut.description}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: 'monospace',
                    backgroundColor: 'action.hover',
                    px: 1,
                    py: 0.25,
                    borderRadius: 0.5,
                  }}
                >
                  {shortcut.keys}
                </Typography>
              </Box>
            ))}
            {sectionIndex < shortcutSections.length - 1 && <Divider sx={{ mt: 1.5 }} />}
          </Box>
        ))}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};
