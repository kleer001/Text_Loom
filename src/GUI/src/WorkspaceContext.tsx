// Workspace Context - Global state management for nodes, connections, and globals

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { NodeResponse, ConnectionResponse, NodeCreateRequest, NodeUpdateRequest } from './types';
import { apiClient } from './apiClient';

interface WorkspaceContextType {
  nodes: NodeResponse[];
  connections: ConnectionResponse[];
  globals: Record<string, string | number | boolean>;
  selectedNodeId: number | null;
  selectedNodeIds: number[];
  loading: boolean;
  error: string | null;
  loadWorkspace: () => Promise<void>;
  selectNode: (sessionId: number | null) => void;
  selectNodes: (sessionIds: number[]) => void;
  getSelectedNode: () => NodeResponse | null;
  getSelectedNodes: () => NodeResponse[];
  createNode: (request: NodeCreateRequest) => Promise<NodeResponse>;
  updateNode: (sessionId: number, request: NodeUpdateRequest) => Promise<NodeResponse>;
  deleteNode: (sessionId: number) => Promise<void>;
  deleteNodes: (sessionIds: number[]) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [connections, setConnections] = useState<ConnectionResponse[]>([]);
  const [globals, setGlobals] = useState<Record<string, string | number | boolean>>({});
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const [selectedNodeIds, setSelectedNodeIds] = useState<number[]>([]);
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
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load workspace';
      setError(message);
      console.error('Workspace load error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectNode = useCallback((sessionId: number | null) => {
    setSelectedNodeId(sessionId);
    setSelectedNodeIds(sessionId !== null ? [sessionId] : []);
  }, []);

  const selectNodes = useCallback((sessionIds: number[]) => {
    setSelectedNodeIds(sessionIds);
    setSelectedNodeId(sessionIds.length === 1 ? sessionIds[0] : null);
  }, []);

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

  const updateNode = useCallback(async (sessionId: number, request: NodeUpdateRequest): Promise<NodeResponse> => {
    console.log('[WorkspaceContext] updateNode called:', {
      sessionId,
      sessionIdType: typeof sessionId,
      request,
      currentNodeCount: nodes.length
    });

    // Find current node to compare
    const currentNode = nodes.find(n => n.session_id === sessionId);
    console.log('[WorkspaceContext] Current node before update:', {
      found: !!currentNode,
      currentSessionId: currentNode?.session_id,
      currentPosition: currentNode?.position
    });

    setLoading(true);
    setError(null);

    try {
      const updatedNode = await apiClient.updateNode(sessionId, request);
      console.log('[WorkspaceContext] updateNode API response:', {
        returnedSessionId: updatedNode.session_id,
        returnedPosition: updatedNode.position,
        requestedSessionId: sessionId,
        sessionIdMatch: updatedNode.session_id === sessionId
      });

      setNodes(prev => prev.map(n => n.session_id === sessionId ? updatedNode : n));
      console.log('[WorkspaceContext] updateNode: state updated successfully');
      return updatedNode;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update node';
      setError(message);
      console.error('[WorkspaceContext] Node update error for session_id:', sessionId, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [nodes]);

  const deleteNode = useCallback(async (sessionId: number): Promise<void> => {
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

  const deleteNodes = useCallback(async (sessionIds: number[]): Promise<void> => {
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