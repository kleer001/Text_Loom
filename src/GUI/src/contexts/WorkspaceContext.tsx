import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import type { WorkspaceState, WorkspaceAction, WorkspaceResponse, NodeData, ConnectionData } from './../types/workspace';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

const workspaceReducer = (state: WorkspaceState, action: WorkspaceAction): WorkspaceState => {
  switch (action.type) {
    case 'SET_WORKSPACE':
      return { ...state, nodes: action.payload.nodes, connections: action.payload.connections, loading: false };
    case 'UPDATE_NODE':
      return { ...state, nodes: state.nodes.map(n => n.path === action.payload.path ? action.payload : n) };
    case 'DELETE_NODE':
      return { ...state, nodes: state.nodes.filter(n => n.path !== action.payload) };
    case 'ADD_CONNECTION':
      return { ...state, connections: [...state.connections, action.payload] };
    case 'DELETE_CONNECTION':
      return { ...state, connections: state.connections.filter(c => c.id !== action.payload) };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    default:
      return state;
  }
};

interface WorkspaceContextValue {
  state: WorkspaceState;
  fetchWorkspace: () => Promise<void>;
  createNode: (type: string, name?: string) => Promise<NodeData | null>;
  updateNodeParameter: (path: string, paramName: string, value: any) => Promise<void>;
  deleteNode: (path: string) => Promise<void>;
  executeNode: (path: string) => Promise<any>;
  createConnection: (source: string, sourceIdx: number, target: string, targetIdx: number) => Promise<void>;
  deleteConnection: (id: string) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export const WorkspaceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(workspaceReducer, {
    nodes: [],
    connections: [],
    loading: true,
    error: null,
  });

  const fetchWorkspace = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/workspace`);
      const data: WorkspaceResponse = await res.json();
      dispatch({ type: 'SET_WORKSPACE', payload: data });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: (err as Error).message });
    }
  }, []);

  const createNode = useCallback(async (type: string, name?: string) => {
    try {
      const res = await fetch(`${API_BASE}/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, name }),
      });
      const node: NodeData = await res.json();
      dispatch({ type: 'UPDATE_NODE', payload: node });
      return node;
    } catch (err) {
      console.error('Failed to create node:', err);
      return null;
    }
  }, []);

  const updateNodeParameter = useCallback(async (path: string, paramName: string, value: any) => {
    try {
      const node = state.nodes.find(n => n.path === path);
      if (!node) return;
      
      const res = await fetch(`${API_BASE}/nodes/${node.session_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parameters: { [paramName]: value } }),
      });
      const updated: NodeData = await res.json();
      dispatch({ type: 'UPDATE_NODE', payload: updated });
    } catch (err) {
      console.error('Failed to update parameter:', err);
    }
  }, [state.nodes]);

  const deleteNode = useCallback(async (path: string) => {
    try {
      const node = state.nodes.find(n => n.path === path);
      if (!node) return;
      
      await fetch(`${API_BASE}/nodes/${node.session_id}`, { method: 'DELETE' });
      dispatch({ type: 'DELETE_NODE', payload: path });
    } catch (err) {
      console.error('Failed to delete node:', err);
    }
  }, [state.nodes]);

  const executeNode = useCallback(async (path: string) => {
    try {
      const node = state.nodes.find(n => n.path === path);
      if (!node) return null;
      
      const res = await fetch(`${API_BASE}/nodes/${node.session_id}/execute`, { method: 'POST' });
      const result = await res.json();
      await fetchWorkspace(); // Refresh to get updated state
      return result;
    } catch (err) {
      console.error('Failed to execute node:', err);
      return null;
    }
  }, [state.nodes, fetchWorkspace]);

  const createConnection = useCallback(async (
    source: string, sourceIdx: number, target: string, targetIdx: number
  ) => {
    try {
      const res = await fetch(`${API_BASE}/connections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_node_path: source,
          source_output_index: sourceIdx,
          target_node_path: target,
          target_input_index: targetIdx,
        }),
      });
      const conn: ConnectionData = await res.json();
      dispatch({ type: 'ADD_CONNECTION', payload: conn });
    } catch (err) {
      console.error('Failed to create connection:', err);
    }
  }, []);

  const deleteConnection = useCallback(async (id: string) => {
    try {
      await fetch(`${API_BASE}/connections/${id}`, { method: 'DELETE' });
      dispatch({ type: 'DELETE_CONNECTION', payload: id });
    } catch (err) {
      console.error('Failed to delete connection:', err);
    }
  }, []);

  // Polling: every 2s when visible
  useEffect(() => {
    fetchWorkspace();
    
    const interval = setInterval(() => {
      if (!document.hidden) {
        fetchWorkspace();
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [fetchWorkspace]);

  return (
    <WorkspaceContext.Provider value={{
      state,
      fetchWorkspace,
      createNode,
      updateNodeParameter,
      deleteNode,
      executeNode,
      createConnection,
      deleteConnection,
    }}>
      {children}
    </WorkspaceContext.Provider>
  );
};

export const useWorkspace = () => {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error('useWorkspace must be used within WorkspaceProvider');
  return ctx;
};