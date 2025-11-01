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
    // Defensive validation - ensure indices are numbers
    if (typeof request.source_output_index !== 'number') {
      console.error('⚠️ CRITICAL: source_output_index is not a number:', request.source_output_index, typeof request.source_output_index);
      throw new Error(`source_output_index must be a number, got ${typeof request.source_output_index}`);
    }
    if (typeof request.target_input_index !== 'number') {
      console.error('⚠️ CRITICAL: target_input_index is not a number:', request.target_input_index, typeof request.target_input_index);
      throw new Error(`target_input_index must be a number, got ${typeof request.target_input_index}`);
    }

    console.log('✓ Creating connection:', {
      from: `${request.source_node_path}[${request.source_output_index}]`,
      to: `${request.target_node_path}[${request.target_input_index}]`,
      types: {
        sourceIndex: typeof request.source_output_index,
        targetIndex: typeof request.target_input_index
      }
    });

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

  async deleteConnectionById(connectionId: string): Promise<void> {
    await this.fetchJson<void>(`/connections/${connectionId}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();
