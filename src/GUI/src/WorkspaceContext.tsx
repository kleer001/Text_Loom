// Workspace Context - Global state management for nodes, connections, and globals

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import type { NodeResponse, ConnectionResponse, NodeCreateRequest, NodeUpdateRequest, ExecutionResponse } from './types';
import { apiClient } from './apiClient';

interface WorkspaceContextType {
  nodes: NodeResponse[];
  connections: ConnectionResponse[];
  globals: Record<string, string | number | boolean>;
  loading: boolean;
  error: string | null;
  loadWorkspace: () => Promise<void>;
  createNode: (request: NodeCreateRequest) => Promise<NodeResponse>;
  updateNode: (sessionId: string, request: NodeUpdateRequest) => Promise<NodeResponse>;
  deleteNode: (sessionId: string) => Promise<void>;
  deleteNodes: (sessionIds: string[]) => Promise<void>;
  executeNode: (sessionId: string) => Promise<ExecutionResponse>;
  setGlobal: (key: string, value: string | number | boolean) => Promise<void>;
  deleteGlobal: (key: string) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [connections, setConnections] = useState<ConnectionResponse[]>([]);
  const [globals, setGlobals] = useState<Record<string, string | number | boolean>>({});
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
  }, []);

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
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete node';
      setError(message);
      console.error('Node deletion error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

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
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete nodes';
      setError(message);
      console.error('Nodes deletion error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const executeNode = useCallback(async (sessionId: string): Promise<ExecutionResponse> => {
    setLoading(true);
    setError(null);

    try {
      // Execute the node
      const executionResult = await apiClient.executeNode(sessionId);

      // Refresh workspace to get updated node states and cook counts
      // This ensures all affected nodes (including dependencies) are updated
      await loadWorkspace();

      return executionResult;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to execute node';
      setError(message);
      console.error('Node execution error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadWorkspace]);

  const setGlobal = useCallback(async (key: string, value: string | number | boolean): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.setGlobal(key, value);
      // Update local state
      setGlobals(prev => ({ ...prev, [key]: value }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to set global variable';
      setError(message);
      console.error('Global set error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteGlobal = useCallback(async (key: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.deleteGlobal(key);
      // Update local state
      setGlobals(prev => {
        const newGlobals = { ...prev };
        delete newGlobals[key];
        return newGlobals;
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete global variable';
      setError(message);
      console.error('Global delete error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value: WorkspaceContextType = {
    nodes,
    connections,
    globals,
    loading,
    error,
    loadWorkspace,
    createNode,
    updateNode,
    deleteNode,
    deleteNodes,
    executeNode,
    setGlobal,
    deleteGlobal,
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
