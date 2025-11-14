// File Browser Dialog - Browse and select files from filesystem

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Breadcrumbs,
  Link,
  Typography,
  CircularProgress,
  Box,
  Alert,
} from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import { apiClient } from './apiClient';

interface FileBrowserDialogProps {
  open: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
  mode: 'file' | 'folder';
  initialPath?: string;
}

interface FileItem {
  id: string;
  name: string;
  path: string;
  is_dir: boolean;
  size: number | null;
}

export const FileBrowserDialog: React.FC<FileBrowserDialogProps> = ({
  open,
  onClose,
  onSelect,
  mode,
  initialPath = '~',
}) => {
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [items, setItems] = useState<FileItem[]>([]);
  const [parentPath, setParentPath] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      loadDirectory(currentPath);
    }
  }, [open, currentPath]);

  const loadDirectory = async (path: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.browseFiles(path);
      setItems(response.items);
      setParentPath(response.parent_path);
      setCurrentPath(response.current_path);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load directory');
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item: FileItem) => {
    if (item.is_dir) {
      // Navigate into directory
      setCurrentPath(item.path);
    } else {
      // Select file
      if (mode === 'file') {
        onSelect(item.path);
        onClose();
      }
    }
  };

  const handleParentClick = () => {
    if (parentPath) {
      setCurrentPath(parentPath);
    }
  };

  const handleSelectFolder = () => {
    if (mode === 'folder') {
      onSelect(currentPath);
      onClose();
    }
  };

  const getPathParts = () => {
    return currentPath.split('/').filter(Boolean);
  };

  const handleBreadcrumbClick = (index: number) => {
    const parts = getPathParts();
    const newPath = '/' + parts.slice(0, index + 1).join('/');
    setCurrentPath(newPath);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Select {mode === 'file' ? 'File' : 'Folder'}
      </DialogTitle>

      <DialogContent>
        {/* Breadcrumb navigation */}
        <Box sx={{ mb: 2 }}>
          <Breadcrumbs>
            {getPathParts().map((part, index) => (
              <Link
                key={index}
                component="button"
                variant="body2"
                onClick={() => handleBreadcrumbClick(index)}
                sx={{ cursor: 'pointer' }}
              >
                {part}
              </Link>
            ))}
          </Breadcrumbs>
        </Box>

        {/* Error display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Loading indicator */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* File/folder list */}
        {!loading && (
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {/* Parent directory option */}
            {parentPath && (
              <ListItemButton onClick={handleParentClick}>
                <ListItemIcon>
                  <ArrowUpwardIcon />
                </ListItemIcon>
                <ListItemText primary=".." secondary="Parent directory" />
              </ListItemButton>
            )}

            {/* Items */}
            {items.length === 0 && !error && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                No items in this directory
              </Typography>
            )}

            {items.map((item) => (
              <ListItemButton
                key={item.id}
                onClick={() => handleItemClick(item)}
                disabled={mode === 'file' && item.is_dir ? false : false}
              >
                <ListItemIcon>
                  {item.is_dir ? <FolderIcon /> : <InsertDriveFileIcon />}
                </ListItemIcon>
                <ListItemText
                  primary={item.name}
                  secondary={
                    item.is_dir
                      ? 'Folder'
                      : item.size
                      ? `${(item.size / 1024).toFixed(1)} KB`
                      : 'File'
                  }
                />
              </ListItemButton>
            ))}
          </List>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {mode === 'folder' && (
          <Button onClick={handleSelectFolder} variant="contained">
            Select Current Folder
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
