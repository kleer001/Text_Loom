// useFileManager Hook - Manages file operations and workspace state

import { useState, useCallback, useEffect, useRef } from 'react';
import { fileManager } from '../services/fileManager';
import { useWorkspace } from '../WorkspaceContext';

const AUTOSAVE_INTERVAL_MS = 30000; // 30 seconds

export interface FileManagerState {
  currentFilePath: string | null;
  isDirty: boolean;
  isSaving: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface FileManagerActions {
  save: () => Promise<void>;
  saveAs: () => Promise<void>;
  open: () => Promise<void>;
  newWorkspace: () => Promise<void>;
  markDirty: () => void;
  markClean: () => void;
}

/**
 * Hook for managing file operations and workspace state
 *
 * Features:
 * - Save/Save-as/Open/New operations
 * - Dirty state tracking
 * - Autosave with debouncing
 * - Error handling
 */
export function useFileManager(): FileManagerState & FileManagerActions {
  const { loadWorkspace, setOnChangeCallback } = useWorkspace();
  const [currentFilePath, setCurrentFilePath] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Autosave timer ref
  const autosaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastAutosaveRef = useRef<number>(0);

  /**
   * Mark workspace as dirty (has unsaved changes)
   */
  const markDirty = useCallback(() => {
    setIsDirty(true);
  }, []);

  /**
   * Mark workspace as clean (no unsaved changes)
   */
  const markClean = useCallback(() => {
    setIsDirty(false);
  }, []);

  /**
   * Perform autosave
   */
  const performAutosave = useCallback(async () => {
    if (!isDirty) {
      return;
    }

    try {
      await fileManager.autosave();
      lastAutosaveRef.current = Date.now();
      console.log('Autosaved workspace');
    } catch (err) {
      console.error('Autosave failed:', err);
    }
  }, [isDirty]);

  /**
   * Schedule autosave (debounced)
   */
  const scheduleAutosave = useCallback(() => {
    // Clear existing timer
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }

    // Schedule new autosave
    autosaveTimerRef.current = setTimeout(() => {
      performAutosave();
    }, AUTOSAVE_INTERVAL_MS);
  }, [performAutosave]);

  /**
   * Save to current file
   */
  const save = useCallback(async () => {
    setIsSaving(true);
    setError(null);

    try {
      const result = await fileManager.save();

      if (result.success && result.filePath) {
        setCurrentFilePath(result.filePath);
        markClean();
        await fileManager.clearAutosave();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save';
      setError(message);
      console.error('Save failed:', err);
    } finally {
      setIsSaving(false);
    }
  }, [markClean]);

  /**
   * Save-as (choose new location)
   */
  const saveAs = useCallback(async () => {
    setIsSaving(true);
    setError(null);

    try {
      const result = await fileManager.saveAs();

      if (result.success && result.filePath) {
        setCurrentFilePath(result.filePath);
        markClean();
        await fileManager.clearAutosave();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save';
      setError(message);
      console.error('Save-as failed:', err);
    } finally {
      setIsSaving(false);
    }
  }, [markClean]);

  /**
   * Open a workspace file
   */
  const open = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fileManager.open();

      if (result.success && result.filePath) {
        setCurrentFilePath(result.filePath);
        markClean();
        await fileManager.clearAutosave();

        // Reload workspace from backend
        await loadWorkspace();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to open file';
      setError(message);
      console.error('Open failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, [loadWorkspace, markClean]);

  /**
   * Create new workspace (clear current)
   */
  const newWorkspace = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await fileManager.newWorkspace();
      setCurrentFilePath(null);
      markClean();
      await fileManager.clearAutosave();

      // Reload workspace from backend (should be empty)
      await loadWorkspace();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create new workspace';
      setError(message);
      console.error('New workspace failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, [loadWorkspace, markClean]);

  /**
   * Setup autosave when workspace becomes dirty
   */
  useEffect(() => {
    if (isDirty) {
      scheduleAutosave();
    }

    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
    };
  }, [isDirty, scheduleAutosave]);

  /**
   * Initialize file path on mount
   */
  useEffect(() => {
    const path = fileManager.getCurrentFilePath();
    if (path) {
      setCurrentFilePath(path);
    }
  }, []);

  /**
   * Set up onChange callback to mark workspace as dirty
   */
  useEffect(() => {
    setOnChangeCallback(() => {
      markDirty();
    });

    return () => {
      setOnChangeCallback(null);
    };
  }, [setOnChangeCallback, markDirty]);

  return {
    // State
    currentFilePath,
    isDirty,
    isSaving,
    isLoading,
    error,

    // Actions
    save,
    saveAs,
    open,
    newWorkspace,
    markDirty,
    markClean,
  };
}
