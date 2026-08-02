import { apiClient } from '@/lib/api/client';
import { ProviderMetadata } from '@/lib/types/settings';

export const ProviderRepository = {
  getAll: async (): Promise<ProviderMetadata[]> => {
    const { data } = await apiClient.get<ProviderMetadata[]>('/providers');
    return data;
  },
  testConnection: async (id: string): Promise<{ success: boolean; latencyMs: number }> => {
    const { data } = await apiClient.post<{ success: boolean; latencyMs: number }>(`/providers/${id}/test`);
    return data;
  }
};
