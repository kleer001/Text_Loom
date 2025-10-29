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
      sessionIdType: typeof sessionId,
      previousSelectedId: selectedNodeId,
      previousSelectedIds: selectedNodeIds,
      totalNodes: nodes.length
    });

    setSelectedNodeId(sessionId);
    setSelectedNodeIds(sessionId !== null ? [sessionId] : []);

    console.log('[SELECTION] State updated:', {
      newSelectedId: sessionId,
      newSelectedIds: sessionId !== null ? [sessionId] : []
    });

    // Sync selection state with backend - only update nodes that changed
    try {
      console.log('[SELECTION] Starting backend sync');
      const updates: Promise<NodeResponse>[] = [];

      // Deselect previously selected nodes that are no longer selected
      const nodesToDeselect = selectedNodeIds.filter(id =>
        sessionId === null || String(id) !== String(sessionId)
      );

      if (nodesToDeselect.length > 0) {
        console.log('[SELECTION] Deselecting nodes:', nodesToDeselect);
        nodesToDeselect.forEach(id => {
          updates.push(apiClient.updateNode(String(id), { selected: false }));
        });
      }

      // Select the target node if provided and not already selected
      if (sessionId !== null && !selectedNodeIds.includes(String(sessionId))) {
        console.log('[SELECTION] Selecting target node:', sessionId);
        updates.push(apiClient.updateNode(String(sessionId), { selected: true }));
      }

      await Promise.all(updates);
      console.log('[SELECTION] Backend sync completed successfully');
    } catch (err) {
      console.error('[SELECTION] Backend sync failed:', err);
    }
  }, [nodes, selectedNodeId, selectedNodeIds]);

  const selectNodes = useCallback(async (sessionIds: string[]) => {
    console.log('[SELECTION] selectNodes called:', {
      sessionIds,
      sessionIdsCount: sessionIds.length,
      sessionIdsTypes: sessionIds.map(id => typeof id),
      previousSelectedIds: selectedNodeIds,
      totalNodes: nodes.length
    });

    // Normalize session IDs to strings for consistent comparison
    const normalizedIds = sessionIds.map(id => String(id));

    setSelectedNodeIds(normalizedIds);
    setSelectedNodeId(normalizedIds.length === 1 ? normalizedIds[0] : null);

    console.log('[SELECTION] Multi-select state updated:', {
      newSelectedIds: normalizedIds,
      newSelectedId: normalizedIds.length === 1 ? normalizedIds[0] : null
    });

    // Sync selection state with backend - only update nodes that changed
    try {
      console.log('[SELECTION] Starting multi-select backend sync');
      const updates: Promise<NodeResponse>[] = [];

      // Deselect previously selected nodes that are no longer selected
      const nodesToDeselect = selectedNodeIds.filter(id =>
        !normalizedIds.includes(String(id))
      );

      if (nodesToDeselect.length > 0) {
        console.log('[SELECTION] Deselecting nodes:', nodesToDeselect);
        nodesToDeselect.forEach(id => {
          updates.push(apiClient.updateNode(String(id), { selected: false }));
        });
      }

      // Select nodes that weren't previously selected
      const nodesToSelect = normalizedIds.filter(id =>
        !selectedNodeIds.includes(String(id))
      );

      if (nodesToSelect.length > 0) {
        console.log('[SELECTION] Selecting nodes:', nodesToSelect);
        nodesToSelect.forEach(id => {
          updates.push(apiClient.updateNode(String(id), { selected: true }));
        });
      }

      await Promise.all(updates);
      console.log('[SELECTION] Multi-select backend sync completed successfully');
    } catch (err) {
      console.error('[SELECTION] Multi-select backend sync failed:', err);
    }
  }, [nodes, selectedNodeIds]);

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
      const newNode = await apiClient.createNode(request);
      setNodes(prev => [...prev, newNode]);
      return newNode;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create node';
      setError(message);
      console.error('Node creation error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

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