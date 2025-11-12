import { useRef, useCallback } from 'react';
import type { Node } from '@xyflow/react';

/**
 * Hook to persist node selection across updates.
 *
 * Industry standard: React Flow recommends storing selected node IDs separately
 * and explicitly restoring them when nodes are recreated from backend updates.
 *
 * This prevents selection loss during:
 * - Parameter changes
 * - Position updates
 * - Node cooking/execution
 * - Workspace reloads
 */
export const useSelectionPersistence = () => {
  const selectedNodeIdsRef = useRef<Set<string>>(new Set());

  /**
   * Capture currently selected node IDs.
   * Call this before operations that might cause nodes to reload.
   */
  const captureSelection = useCallback((nodes: Node[]) => {
    const selectedIds = nodes
      .filter(node => node.selected)
      .map(node => node.id);

    selectedNodeIdsRef.current = new Set(selectedIds);
  }, []);

  /**
   * Restore selection to nodes that were previously selected.
   * Call this when applying new nodes from backend updates.
   *
   * @param nodes - The new nodes array to restore selection to
   * @returns The nodes array with selection restored
   */
  const restoreSelection = useCallback((nodes: Node[]): Node[] => {
    if (selectedNodeIdsRef.current.size === 0) {
      return nodes;
    }

    return nodes.map(node => ({
      ...node,
      selected: selectedNodeIdsRef.current.has(node.id)
    }));
  }, []);

  /**
   * Clear tracked selection.
   * Call this when selection should be intentionally cleared.
   */
  const clearSelection = useCallback(() => {
    selectedNodeIdsRef.current.clear();
  }, []);

  /**
   * Check if a node ID is in the tracked selection.
   */
  const isSelected = useCallback((nodeId: string): boolean => {
    return selectedNodeIdsRef.current.has(nodeId);
  }, []);

  return {
    captureSelection,
    restoreSelection,
    clearSelection,
    isSelected
  };
};
