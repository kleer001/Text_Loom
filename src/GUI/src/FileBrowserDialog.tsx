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

const formatFileSize = (bytes: number | null): string => {
  if (!bytes) return 'File';
  return `${(bytes / 1024).toFixed(1)} KB`;
};

const getItemSecondary = (item: FileItem): string =>
  item.is_dir ? 'Folder' : formatFileSize(item.size);

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
      setCurrentPath(initialPath);
      setError(null);
    }
  }, [open, initialPath]);

  useEffect(() => {
    if (!open) return;

    const loadDirectory = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.browseFiles(currentPath);
        setItems(response.items);
        setParentPath(response.parent_path);
        setCurrentPath(response.current_path);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load directory');
      } finally {
        setLoading(false);
      }
    };

    loadDirectory();
  }, [open, currentPath]);

  const handleItemClick = (item: FileItem) => {
    if (item.is_dir) {
      setCurrentPath(item.path);
      return;
    }

    if (mode === 'file') {
      onSelect(item.path);
      onClose();
    }
  };

  const handleParentClick = () => parentPath && setCurrentPath(parentPath);

  const handleSelectFolder = () => {
    if (mode === 'folder') {
      onSelect(currentPath);
      onClose();
    }
  };

  const pathParts = currentPath.split('/').filter(Boolean);

  const handleBreadcrumbClick = (index: number) => {
    const newPath = '/' + pathParts.slice(0, index + 1).join('/');
    setCurrentPath(newPath);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Select {mode === 'file' ? 'File' : 'Folder'}</DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Breadcrumbs>
            {pathParts.map((part, index) => (
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

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {!loading && (
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {parentPath && (
              <ListItemButton onClick={handleParentClick}>
                <ListItemIcon><ArrowUpwardIcon /></ListItemIcon>
                <ListItemText primary=".." secondary="Parent directory" />
              </ListItemButton>
            )}

            {items.length === 0 && !error && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                No items in this directory
              </Typography>
            )}

            {items.map((item) => (
              <ListItemButton key={item.id} onClick={() => handleItemClick(item)}>
                <ListItemIcon>
                  {item.is_dir ? <FolderIcon /> : <InsertDriveFileIcon />}
                </ListItemIcon>
                <ListItemText
                  primary={item.name}
                  secondary={getItemSecondary(item)}
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
