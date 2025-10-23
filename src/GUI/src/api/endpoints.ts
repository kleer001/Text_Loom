// src/GUI/src/api/endpoints.ts

import { apiClient } from './client';
import type { NodeData, ConnectionData } from '../types/workspace';

export const fetchWorkspace = async () => {
  const response = await apiClient.get('/workspace');
  return response.data;
};

export const fetchAvailableNodeTypes = async (): Promise<string[]> => {
  const response = await apiClient.get('/nodes');
  const nodes = response.data;
  // Extract unique node types from existing nodes
  const types = [...new Set(nodes.map((n: NodeData) => n.type))];
  return types.sort();
};

export const createNode = async (data: { type: string; position: [number, number]; name?: string }) => {
  const response = await apiClient.post('/nodes', data);
  return response.data;
};

export const updateNode = async (sessionId: number, data: { parameters?: Record<string, any>; position?: [number, number] }) => {
  const response = await apiClient.put(`/nodes/${sessionId}`, data);
  return response.data;
};

export const deleteNode = async (sessionId: number) => {
  await apiClient.delete(`/nodes/${sessionId}`);
};

export const executeNode = async (sessionId: number) => {
  const response = await apiClient.post(`/nodes/${sessionId}/execute`);
  return response.data;
};

export const createConnection = async (data: Omit<ConnectionData, 'id'>) => {
  const response = await apiClient.post('/connections', data);
  return response.data;
};

export const deleteConnection = async (id: string) => {
  await apiClient.delete(`/connections/${id}`);
};