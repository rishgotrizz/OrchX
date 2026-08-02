import { apiClient } from '@/lib/api/client';
import { OrchXDocument } from '@/lib/types/document';

export const DocumentsRepository = {
  getAll: async (): Promise<OrchXDocument[]> => {
    const { data } = await apiClient.get<OrchXDocument[]>('/documents');
    return data;
  },
  getById: async (id: string): Promise<OrchXDocument> => {
    const { data } = await apiClient.get<OrchXDocument>(`/documents/${id}`);
    return data;
  },
  create: async (payload: Partial<OrchXDocument>): Promise<OrchXDocument> => {
    const { data } = await apiClient.post<OrchXDocument>('/documents', payload);
    return data;
  },
  update: async (id: string, payload: Partial<OrchXDocument>): Promise<OrchXDocument> => {
    const { data } = await apiClient.patch<OrchXDocument>(`/documents/${id}`, payload);
    return data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  }
};
