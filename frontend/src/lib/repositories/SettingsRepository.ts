import { apiClient } from '@/lib/api/client';

export const SettingsRepository = {
  getGlobalProfile: async (): Promise<Record<string, any>> => {
    const { data } = await apiClient.get<Record<string, any>>('/settings/global');
    return data;
  },
  updateGlobalProfile: async (payload: Record<string, any>): Promise<Record<string, any>> => {
    const { data } = await apiClient.patch<Record<string, any>>('/settings/global', payload);
    return data;
  }
};
