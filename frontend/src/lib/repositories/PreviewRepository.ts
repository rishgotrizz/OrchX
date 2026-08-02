import { apiClient } from '@/lib/api/client';
import * as PreviewTypes from '@/lib/types/preview';

export const PreviewRepository = {
  getArtifacts: async () => (await apiClient.get<PreviewTypes.Artifact[]>('/preview/artifacts')).data,
  getArtifactById: async (id: string) => (await apiClient.get<PreviewTypes.Artifact>(`/preview/artifacts/${id}`)).data,
};
