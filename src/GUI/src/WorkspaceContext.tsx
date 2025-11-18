// Workspace Context - Global state management for nodes, connections, and globals

import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import type { NodeResponse, ConnectionResponse, NodeCreateRequest, NodeUpdateRequest, ExecutionResponse } from './types';
import { apiClient } from './apiClient';
import { DESELECTION_DELAY_MS } from './constants';

interface WorkspaceContextType {
  nodes: NodeResponse[];
  connections: ConnectionResponse[];
  globals: Record<string, string | number | boolean>;
  loading: boolean;
  error: string | null;
  executingNodeId: string | null;
  newlyCreatedNodeId: string | null;
  lastExecutionResult: ExecutionResponse | null;
  lastExecutedNodeName: string | null;
  loadWorkspace: () => Promise<void>;
  createNode: (request: NodeCreateRequest) => Promise<NodeResponse[]>;
  updateNode: (sessionId: string, request: NodeUpdateRequest) => Promise<NodeResponse[]>;
  deleteNode: (sessionId: string) => Promise<void>;
  deleteNodes: (sessionIds: string[]) => Promise<void>;
  executeNode: (sessionId: string) => Promise<ExecutionResponse>;
  clearExecutionResult: () => void;
  setGlobal: (key: string, value: string | number | boolean) => Promise<void>;
  deleteGlobal: (key: string) => Promise<void>;
  setOnChangeCallback: (callback: (() => void) | null) => void;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [nodes, setNodes] = useState<NodeResponse[]>([]);
  const [connections, setConnections] = useState<ConnectionResponse[]>([]);
  const [globals, setGlobals] = useState<Record<string, string | number | boolean>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [executingNodeId, setExecutingNodeId] = useState<string | null>(null);
  const [newlyCreatedNodeId, setNewlyCreatedNodeId] = useState<string | null>(null);
  const [lastExecutionResult, setLastExecutionResult] = useState<ExecutionResponse | null>(null);
  const [lastExecutedNodeName, setLastExecutedNodeName] = useState<string | null>(null);
  const onChangeCallbackRef = useRef<(() => void) | null>(null);

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

  const createNode = useCallback(async (request: NodeCreateRequest): Promise<NodeResponse[]> => {
    setLoading(true);
    setError(null);

    try {
      const newNodes = await apiClient.createNode(request);

      // For loopers, newNodes will include the looper + inputNull + outputNull
      // For regular nodes, newNodes will have just the one node
      setNewlyCreatedNodeId(newNodes[0].session_id);

      // Add all new nodes instead of reloading entire workspace
      // This preserves viewport and is more efficient
      setNodes(prev => [...prev, ...newNodes]);

      setTimeout(() => setNewlyCreatedNodeId(null), DESELECTION_DELAY_MS);
      onChangeCallbackRef.current?.();

      return newNodes;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create node';
      setError(message);
      console.error('Node creation error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateNode = useCallback(async (sessionId: string, request: NodeUpdateRequest): Promise<NodeResponse[]> => {
    try {
      const updatedNodes = await apiClient.updateNode(sessionId, request);
      const updateMap = new Map(updatedNodes.map(n => [n.session_id, n]));
      setNodes(prev => prev.map(n => updateMap.get(n.session_id) || n));
      onChangeCallbackRef.current?.();

      return updatedNodes;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update node';
      setError(message);
      console.error('Node update error for session_id:', sessionId, err);
      throw err;
    }
  }, []);

  const deleteNode = useCallback(async (sessionId: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.deleteNode(sessionId);
      setNodes(prev => prev.filter(n => n.session_id !== sessionId));
      setConnections(prev => prev.filter(c =>
        c.source_node_session_id !== sessionId && c.target_node_session_id !== sessionId
      ));
      onChangeCallbackRef.current?.();
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
      await Promise.all(sessionIds.map(id => apiClient.deleteNode(id)));

      setNodes(prev => prev.filter(n => !sessionIds.includes(n.session_id)));
      setConnections(prev => prev.filter(c =>
        !sessionIds.includes(c.source_node_session_id) &&
        !sessionIds.includes(c.target_node_session_id)
      ));
      onChangeCallbackRef.current?.();
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
    setExecutingNodeId(sessionId);

    try {
      const node = nodes.find(n => n.session_id === sessionId);
      const nodeName = node?.name || 'Unknown Node';

      const executionResult = await apiClient.executeNode(sessionId);

      setLastExecutionResult(executionResult);
      setLastExecutedNodeName(nodeName);

      await loadWorkspace();

      setTimeout(() => setExecutingNodeId(null), DESELECTION_DELAY_MS);

      return executionResult;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to execute node';
      setError(message);
      console.error('Node execution error:', err);
      setExecutingNodeId(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadWorkspace, nodes]);

  const setGlobal = useCallback(async (key: string, value: string | number | boolean): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.setGlobal(key, value);
      setGlobals(prev => ({ ...prev, [key]: value }));
      onChangeCallbackRef.current?.();
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
      setGlobals(({ [key]: _, ...rest }) => rest);
      onChangeCallbackRef.current?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete global variable';
      setError(message);
      console.error('Global delete error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearExecutionResult = useCallback(() => {
    setLastExecutionResult(null);
    setLastExecutedNodeName(null);
  }, []);

  const setOnChange = useCallback((callback: (() => void) | null) => {
    onChangeCallbackRef.current = callback;
  }, []);

  const value: WorkspaceContextType = {
    nodes,
    connections,
    globals,
    loading,
    error,
    executingNodeId,
    newlyCreatedNodeId,
    lastExecutionResult,
    lastExecutedNodeName,
    loadWorkspace,
    createNode,
    updateNode,
    deleteNode,
    deleteNodes,
    executeNode,
    clearExecutionResult,
    setGlobal,
    deleteGlobal,
    setOnChangeCallback: setOnChange,
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
