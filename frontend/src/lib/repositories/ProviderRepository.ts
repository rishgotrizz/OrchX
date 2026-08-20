import { apiClient } from '@/lib/api/client';
import { ProviderMetadata } from '@/lib/types/settings';

/**
 * ProviderRepository
 *
 * All credential operations go to /vault/providers (the SecretVault backend router).
 * The /providers route returns public provider metadata only (no credentials).
 */
export const ProviderRepository = {
  // Get public provider metadata (no credentials returned)
  getAll: async (): Promise<ProviderMetadata[]> => {
    const { data } = await apiClient.get<ProviderMetadata[]>('/providers');
    return data;
  },

  // Test a provider's connectivity
  testConnection: async (id: string): Promise<{ success: boolean; latencyMs: number }> => {
    const { data } = await apiClient.post<{ success: boolean; latencyMs: number }>(`/providers/${id}/test`);
    return data;
  },

  // Store credentials in the SecretVault — sends to /vault/providers (correct backend route)
  storeCredentials: async (provider: string, apiKey: string): Promise<{ status: string; message: string }> => {
    const { data } = await apiClient.post<{ status: string; message: string }>('/vault/providers', {
      provider,
      credentials: { api_key: apiKey }
    });
    return data;
  },

  // Delete provider credentials from SecretVault
  deleteCredentials: async (provider: string): Promise<{ status: string; message: string }> => {
    const { data } = await apiClient.delete<{ status: string; message: string }>(`/vault/providers/${provider}`);
    return data;
  },

  // Check which providers have credentials configured (safe metadata only)
  getConfiguredProviders: async (): Promise<Record<string, { configured: boolean }>> => {
    // This reads from localStorage-backed MSW or real backend status endpoint
    try {
      const { data } = await apiClient.get<Record<string, { configured: boolean }>>('/providers/status');
      return data;
    } catch {
      // Gracefully fall back to localStorage if backend doesn't have this route yet
      if (typeof window === 'undefined') return {};
      const stored = JSON.parse(localStorage.getItem('orchx_user_credentials') || '{}');
      const result: Record<string, { configured: boolean }> = {};
      Object.keys(stored).forEach(k => {
        const v = stored[k];
        result[k] = { configured: !!(v && (v === 'configured' || v.configured === true || (typeof v === 'string' && v.trim() !== ''))) };
      });
      return result;
    }
  }
};
