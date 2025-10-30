// Workspace Context - Global state management for nodes, connections, and globals

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { NodeResponse, ConnectionResponse, NodeCreateRequest, NodeUpdateRequest } from './types';
import { apiClient } from './apiClient';

interface WorkspaceContextType {
  nodes: NodeResponse[];
  connections: ConnectionResponse[];
  globals: Record<string, string | number | boolean>;
  selectedNodeId: string | null;
  selectedNodeIds: string[];
  loading: boolean;
  error: string | null;
  loadWorkspace: () => Promise<void>;
  selectNode: (sessionId: string | null) => Promise<void>;
  selectNodes: (sessionIds: string[]) => Promise<void>;
  getSelectedNode: () => NodeResponse | null;
  getSelectedNodes: () => NodeResponse[];
  createNode: (request: NodeCreateRequest) => Promise<NodeResponse>;
  updateNode: (sessionId: string, request: NodeUpdateRequest) => Promise<NodeResponse>;
  deleteNode: (sessionId: string) => Promise<void>;
  deleteNodes: (sessionIds: string[]) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [connections, setConnections] = useState<ConnectionResponse[]>([]);
  const [globals, setGlobals] = useState<Record<string, string | number | boolean>>({});
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const workspace = await apiClient.getWorkspace();
      setNodes(workspace.nodes);
      setConnections(workspace.connections);
      setGlobals(workspace.globals);

      // Restore selection state from backend
      const selectedNodes = workspace.nodes
        .filter(node => node.selected)
        .map(node => String(node.session_id));

      console.log('[SELECTION] Restoring selection from workspace:', {
        selectedNodes,
        selectedCount: selectedNodes.length
      });

      setSelectedNodeIds(selectedNodes);
      setSelectedNodeId(selectedNodes.length === 1 ? selectedNodes[0] : null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load workspace';
      setError(message);
      console.error('Workspace load error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectNode = useCallback(async (sessionId: string | null) => {
    console.log('[SELECTION] selectNode called:', {
      sessionId,
      previousSelectedId: selectedNodeId,
      previousSelectedIds: selectedNodeIds
    });

    // OPTIMISTIC UPDATE: Update local state immediately for instant UI response
    const previousIds = selectedNodeIds;
    setSelectedNodeId(sessionId);
    setSelectedNodeIds(sessionId !== null ? [sessionId] : []);

    // Update nodes array to reflect selection visually
    setNodes(prev => prev.map(n => ({
      ...n,
      selected: sessionId !== null && String(n.session_id) === String(sessionId)
    })));

    console.log('[SELECTION] Local state updated instantly');

    // Background sync with backend (don't await - fire and forget with error handling)
    const syncBackend = async () => {
      try {
        const updates: Promise<NodeResponse>[] = [];

        // Deselect previously selected nodes
        const nodesToDeselect = previousIds.filter(id =>
          sessionId === null || String(id) !== String(sessionId)
        );

        if (nodesToDeselect.length > 0) {
          console.log('[SELECTION] Backend: Deselecting', nodesToDeselect);
          nodesToDeselect.forEach(id => {
            updates.push(apiClient.updateNode(String(id), { selected: false }));
          });
        }

        // Select the target node if not already selected
        if (sessionId !== null && !previousIds.includes(String(sessionId))) {
          console.log('[SELECTION] Backend: Selecting', sessionId);
          updates.push(apiClient.updateNode(String(sessionId), { selected: true }));
        }

        await Promise.all(updates);
        console.log('[SELECTION] Backend sync completed');
      } catch (err) {
        console.error('[SELECTION] Backend sync failed:', err);
        // Optionally: revert optimistic update on failure
      }
    };

    syncBackend(); // Fire and forget
  }, [selectedNodeId, selectedNodeIds]);

  const selectNodes = useCallback(async (sessionIds: string[]) => {
    console.log('[SELECTION] selectNodes called:', {
      sessionIds,
      previousSelectedIds: selectedNodeIds
    });

    // Normalize session IDs to strings
    const normalizedIds = sessionIds.map(id => String(id));
    const previousIds = selectedNodeIds;

    // OPTIMISTIC UPDATE: Update local state immediately
    setSelectedNodeIds(normalizedIds);
    setSelectedNodeId(normalizedIds.length === 1 ? normalizedIds[0] : null);

    // Update nodes array to reflect selection visually
    setNodes(prev => prev.map(n => ({
      ...n,
      selected: normalizedIds.includes(String(n.session_id))
    })));

    console.log('[SELECTION] Multi-select local state updated instantly');

    // Background sync with backend
    const syncBackend = async () => {
      try {
        const updates: Promise<NodeResponse>[] = [];

        // Deselect nodes no longer selected
        const nodesToDeselect = previousIds.filter(id =>
          !normalizedIds.includes(String(id))
        );

        if (nodesToDeselect.length > 0) {
          console.log('[SELECTION] Backend: Deselecting', nodesToDeselect);
          nodesToDeselect.forEach(id => {
            updates.push(apiClient.updateNode(String(id), { selected: false }));
          });
        }

        // Select newly selected nodes
        const nodesToSelect = normalizedIds.filter(id =>
          !previousIds.includes(String(id))
        );

        if (nodesToSelect.length > 0) {
          console.log('[SELECTION] Backend: Selecting', nodesToSelect);
          nodesToSelect.forEach(id => {
            updates.push(apiClient.updateNode(String(id), { selected: true }));
          });
        }

        await Promise.all(updates);
        console.log('[SELECTION] Multi-select backend sync completed');
      } catch (err) {
        console.error('[SELECTION] Multi-select backend sync failed:', err);
      }
    };

    syncBackend(); // Fire and forget
  }, [selectedNodeIds]);

  const getSelectedNode = useCallback(() => {
    if (selectedNodeId === null) return null;
    return nodes.find(n => n.session_id === selectedNodeId) || null;
  }, [nodes, selectedNodeId]);

  const getSelectedNodes = useCallback(() => {
    return nodes.filter(n => selectedNodeIds.includes(n.session_id));
  }, [nodes, selectedNodeIds]);

  const createNode = useCallback(async (request: NodeCreateRequest): Promise<NodeResponse> => {
    setLoading(true);
    setError(null);

    try {
      console.log('[CREATE_NODE] Creating new node:', request);
      const newNode = await apiClient.createNode(request);
      console.log('[CREATE_NODE] Node created with session_id:', newNode.session_id, 'selected:', newNode.selected);

      // Deselect all previously selected nodes in backend
      if (selectedNodeIds.length > 0) {
        console.log('[CREATE_NODE] Deselecting previous nodes:', selectedNodeIds);
        await Promise.all(
          selectedNodeIds.map(id => apiClient.updateNode(String(id), { selected: false }))
        );
      }

      // Update nodes array with new node
      setNodes(prev => {
        // Deselect all existing nodes locally
        const updatedNodes = prev.map(n => ({ ...n, selected: false }));
        return [...updatedNodes, newNode];
      });

      // Update selection state to new node only
      const newNodeId = String(newNode.session_id);
      console.log('[CREATE_NODE] Setting selection to new node:', newNodeId);
      setSelectedNodeId(newNodeId);
      setSelectedNodeIds([newNodeId]);

      return newNode;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create node';
      setError(message);
      console.error('Node creation error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [selectedNodeIds]);

  const updateNode = useCallback(async (sessionId: string, request: NodeUpdateRequest): Promise<NodeResponse> => {
    setLoading(true);
    setError(null);

    try {
      const updatedNode = await apiClient.updateNode(sessionId, request);
      setNodes(prev => prev.map(n => n.session_id === sessionId ? updatedNode : n));
      return updatedNode;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update node';
      setError(message);
      console.error('Node update error for session_id:', sessionId, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [nodes]);

  const deleteNode = useCallback(async (sessionId: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.deleteNode(sessionId);
      setNodes(prev => prev.filter(n => n.session_id !== sessionId));
      // Also remove connections involving this node
      setConnections(prev => prev.filter(c =>
        c.source_node_session_id !== sessionId && c.target_node_session_id !== sessionId
      ));
      // Clear selection if the deleted node was selected
      if (selectedNodeId === sessionId) {
        setSelectedNodeId(null);
        setSelectedNodeIds([]);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete node';
      setError(message);
      console.error('Node deletion error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [selectedNodeId]);

  const deleteNodes = useCallback(async (sessionIds: string[]): Promise<void> => {
    if (sessionIds.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      // Delete all nodes in parallel
      await Promise.all(sessionIds.map(id => apiClient.deleteNode(id)));

      // Update state
      setNodes(prev => prev.filter(n => !sessionIds.includes(n.session_id)));
      setConnections(prev => prev.filter(c =>
        !sessionIds.includes(c.source_node_session_id) &&
        !sessionIds.includes(c.target_node_session_id)
      ));

      // Clear selection
      setSelectedNodeId(null);
      setSelectedNodeIds([]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete nodes';
      setError(message);
      console.error('Nodes deletion error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value: WorkspaceContextType = {
    nodes,
    connections,
    globals,
    selectedNodeId,
    selectedNodeIds,
    loading,
    error,
    loadWorkspace,
    selectNode,
    selectNodes,
    getSelectedNode,
    getSelectedNodes,
    createNode,
    updateNode,
    deleteNode,
    deleteNodes,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};

export const useWorkspace = (): WorkspaceContextType => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within WorkspaceProvider');
  }
  return context;
};