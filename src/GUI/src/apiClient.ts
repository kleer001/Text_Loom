// API Client Service - Handles all backend communication

import type {
  WorkspaceState,
  ApiError,
  NodeResponse,
  NodeCreateRequest,
  NodeUpdateRequest,
  ConnectionRequest,
  ConnectionResponse,
  ConnectionDeleteRequest
} from './types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiClient {
  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        console.error('[API Error]', {
          status: response.status,
          url,
          method: options?.method,
          requestBody: options?.body,
          error,
        });
        throw new Error(error.message || `API Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }

  async getWorkspace(): Promise<WorkspaceState> {
    return this.fetchJson<WorkspaceState>('/workspace');
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.fetchJson<{ status: string }>('/');
  }

  // Node operations
  async createNode(request: NodeCreateRequest): Promise<NodeResponse> {
    return this.fetchJson<NodeResponse>('/nodes', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async updateNode(sessionId: string, request: NodeUpdateRequest): Promise<NodeResponse> {
    return this.fetchJson<NodeResponse>(`/nodes/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  }

  async deleteNode(sessionId: string): Promise<void> {
    await this.fetchJson<void>(`/nodes/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getNode(sessionId: string): Promise<NodeResponse> {
    return this.fetchJson<NodeResponse>(`/nodes/${sessionId}`);
  }

  async listNodes(): Promise<NodeResponse[]> {
    return this.fetchJson<NodeResponse[]>('/nodes');
  }

  // Connection operations
  async createConnection(request: ConnectionRequest): Promise<ConnectionResponse> {
    return this.fetchJson<ConnectionResponse>('/connections', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async deleteConnection(request: ConnectionDeleteRequest): Promise<void> {
    await this.fetchJson<void>('/connections', {
      method: 'DELETE',
      body: JSON.stringify(request),
    });
  }
}

export const apiClient = new ApiClient();
