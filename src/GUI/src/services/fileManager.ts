// File Manager Service - Handles all file I/O operations for Text Loom workspaces
// Uses File System Access API with fallback to download/upload

import { apiClient } from '../apiClient';
import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface AutosaveDB extends DBSchema {
  autosave: {
    key: string;
    value: {
      flowstateData: Record<string, any>;
      timestamp: number;
      currentFilePath: string | null;
    };
  };
}

const AUTOSAVE_KEY = 'workspace_autosave';
const DB_NAME = 'TextLoomDB';
const DB_VERSION = 1;

// Browser File System Access API types
interface FileSystemFileHandle {
  getFile(): Promise<File>;
  createWritable(): Promise<FileSystemWritableFileStream>;
  name: string;
}

interface FileSystemWritableFileStream extends WritableStream {
  write(data: string | BufferSource | Blob): Promise<void>;
  close(): Promise<void>;
}

declare global {
  interface Window {
    showSaveFilePicker?: (options?: any) => Promise<FileSystemFileHandle>;
    showOpenFilePicker?: (options?: any) => Promise<FileSystemFileHandle[]>;
  }
}

/**
 * FileManager - Single Responsibility: Handle all file I/O for workspaces
 *
 * Features:
 * - Save/Save-as using File System Access API
 * - Open files
 * - Autosave to IndexedDB
 * - Fallback to download/upload for unsupported browsers
 */
export class FileManager {
  private db: IDBPDatabase<AutosaveDB> | null = null;
  private fileHandle: FileSystemFileHandle | null = null;
  private currentFilePath: string | null = null;

  constructor() {
    this.initDB();
  }

  /**
   * Initialize IndexedDB for autosave
   */
  private async initDB() {
    try {
      this.db = await openDB<AutosaveDB>(DB_NAME, DB_VERSION, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('autosave')) {
            db.createObjectStore('autosave');
          }
        },
      });
    } catch (error) {
      console.error('Failed to initialize IndexedDB:', error);
    }
  }

  /**
   * Check if File System Access API is supported
   */
  isFileSystemAccessSupported(): boolean {
    return 'showSaveFilePicker' in window && 'showOpenFilePicker' in window;
  }

  /**
   * Save workspace to current file (uses file handle if available)
   * If no file handle, triggers Save-as
   */
  async save(): Promise<{ success: boolean; filePath: string | null }> {
    if (this.fileHandle) {
      return this.saveToHandle(this.fileHandle);
    } else {
      return this.saveAs();
    }
  }

  /**
   * Save-as: Show file picker and save to selected location
   */
  async saveAs(): Promise<{ success: boolean; filePath: string | null }> {
    if (this.isFileSystemAccessSupported()) {
      return this.saveAsWithFileSystemAPI();
    } else {
      return this.saveAsWithDownload();
    }
  }

  /**
   * Save using File System Access API
   */
  private async saveAsWithFileSystemAPI(): Promise<{ success: boolean; filePath: string | null }> {
    try {
      // Show save file picker
      const handle = await window.showSaveFilePicker!({
        types: [
          {
            description: 'Text Loom Workspace',
            accept: { 'application/json': ['.tl'] },
          },
        ],
        suggestedName: 'workspace.tl',
      });

      this.fileHandle = handle;
      return this.saveToHandle(handle);
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // User cancelled
        return { success: false, filePath: null };
      }
      console.error('Save-as failed:', error);
      throw error;
    }
  }

  /**
   * Save to a specific file handle
   */
  private async saveToHandle(handle: FileSystemFileHandle): Promise<{ success: boolean; filePath: string }> {
    try {
      // Export workspace from backend
      const flowstateData = await apiClient.exportWorkspace();

      // Write to file
      const writable = await handle.createWritable();
      await writable.write(JSON.stringify(flowstateData, null, 2));
      await writable.close();

      this.currentFilePath = handle.name;

      return {
        success: true,
        filePath: handle.name,
      };
    } catch (error) {
      console.error('Failed to save to file handle:', error);
      throw error;
    }
  }

  /**
   * Fallback: Save by downloading file
   */
  private async saveAsWithDownload(): Promise<{ success: boolean; filePath: string }> {
    try {
      // Export workspace from backend
      const flowstateData = await apiClient.exportWorkspace();

      // Create blob and download
      const blob = new Blob([JSON.stringify(flowstateData, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'workspace.tl';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      const filePath = 'workspace.tl';
      this.currentFilePath = filePath;

      return {
        success: true,
        filePath,
      };
    } catch (error) {
      console.error('Failed to download file:', error);
      throw error;
    }
  }

  /**
   * Open a workspace file
   */
  async open(): Promise<{ success: boolean; filePath: string | null }> {
    if (this.isFileSystemAccessSupported()) {
      return this.openWithFileSystemAPI();
    } else {
      return this.openWithUpload();
    }
  }

  /**
   * Open using File System Access API
   */
  private async openWithFileSystemAPI(): Promise<{ success: boolean; filePath: string }> {
    try {
      // Show open file picker
      const [handle] = await window.showOpenFilePicker!({
        types: [
          {
            description: 'Text Loom Workspace',
            accept: { 'application/json': ['.tl'] },
          },
        ],
        multiple: false,
      });

      this.fileHandle = handle;

      // Read file
      const file = await handle.getFile();
      const text = await file.text();
      const flowstateData = JSON.parse(text);

      // Import to backend
      await apiClient.importWorkspace(flowstateData);

      this.currentFilePath = handle.name;

      return {
        success: true,
        filePath: handle.name,
      };
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // User cancelled
        return { success: false, filePath: null };
      }
      console.error('Open failed:', error);
      throw error;
    }
  }

  /**
   * Fallback: Open by uploading file
   */
  private async openWithUpload(): Promise<{ success: boolean; filePath: string | null }> {
    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.tl,application/json';

      input.onchange = async (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) {
          resolve({ success: false, filePath: null });
          return;
        }

        try {
          const text = await file.text();
          const flowstateData = JSON.parse(text);

          // Import to backend
          await apiClient.importWorkspace(flowstateData);

          this.currentFilePath = file.name;

          resolve({
            success: true,
            filePath: file.name,
          });
        } catch (error) {
          console.error('Failed to open file:', error);
          reject(error);
        }
      };

      input.click();
    });
  }

  /**
   * Create a new workspace (clear current)
   */
  async newWorkspace(): Promise<void> {
    await apiClient.clearWorkspace();
    this.fileHandle = null;
    this.currentFilePath = null;
  }

  /**
   * Autosave workspace to IndexedDB
   */
  async autosave(): Promise<void> {
    if (!this.db) {
      console.warn('IndexedDB not initialized, skipping autosave');
      return;
    }

    try {
      const flowstateData = await apiClient.exportWorkspace();

      await this.db.put('autosave', {
        flowstateData,
        timestamp: Date.now(),
        currentFilePath: this.currentFilePath,
      }, AUTOSAVE_KEY);
    } catch (error) {
      console.error('Autosave failed:', error);
    }
  }

  /**
   * Get autosave data if it exists
   */
  async getAutosave(): Promise<{
    flowstateData: Record<string, any>;
    timestamp: number;
    currentFilePath: string | null;
  } | null> {
    if (!this.db) {
      return null;
    }

    try {
      const data = await this.db.get('autosave', AUTOSAVE_KEY);
      return data || null;
    } catch (error) {
      console.error('Failed to get autosave:', error);
      return null;
    }
  }

  /**
   * Clear autosave data
   */
  async clearAutosave(): Promise<void> {
    if (!this.db) {
      return;
    }

    try {
      await this.db.delete('autosave', AUTOSAVE_KEY);
    } catch (error) {
      console.error('Failed to clear autosave:', error);
    }
  }

  /**
   * Get current file path
   */
  getCurrentFilePath(): string | null {
    return this.currentFilePath;
  }

  /**
   * Check if there's a current file
   */
  hasCurrentFile(): boolean {
    return this.fileHandle !== null || this.currentFilePath !== null;
  }

  /**
   * Set current file path (used when restoring from autosave)
   */
  setCurrentFilePath(path: string | null): void {
    this.currentFilePath = path;
  }
}

// Singleton instance
export const fileManager = new FileManager();
