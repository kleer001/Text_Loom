// API Client Service - Handles all backend communication

import type {
  WorkspaceState,
  ApiError,
  NodeResponse,
  NodeCreateRequest,
  NodeUpdateRequest
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

  async updateNode(sessionId: number, request: NodeUpdateRequest): Promise<NodeResponse> {
    console.log('[ApiClient] updateNode called:', {
      sessionId,
      sessionIdType: typeof sessionId,
      url: `/nodes/${sessionId}`,
      request
    });

    const response = await this.fetchJson<NodeResponse>(`/nodes/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });

    console.log('[ApiClient] updateNode response received:', {
      requestedSessionId: sessionId,
      responseSessionId: response.session_id,
      responsePosition: response.position,
      sessionIdMatch: response.session_id === sessionId
    });

    return response;
  }

  async deleteNode(sessionId: number): Promise<void> {
    await this.fetchJson<void>(`/nodes/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getNode(sessionId: number): Promise<NodeResponse> {
    return this.fetchJson<NodeResponse>(`/nodes/${sessionId}`);
  }

  async listNodes(): Promise<NodeResponse[]> {
    return this.fetchJson<NodeResponse[]>('/nodes');
  }
}

export const apiClient = new ApiClient();
