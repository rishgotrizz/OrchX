import { apiClient } from '@/lib/api/client';

export const MissionRepository = {
  getTelemetry: async () => (await apiClient.get('/mission/telemetry')).data,
  getWorkflow: async () => (await apiClient.get('/mission/workflow')).data,
  getTasks: async () => (await apiClient.get('/mission/tasks')).data,
  getSessions: async () => (await apiClient.get('/mission/sessions')).data,
  getActivity: async () => (await apiClient.get('/mission/activity')).data,
  getCredits: async () => (await apiClient.get('/mission/credits')).data,
  getSuggestions: async () => (await apiClient.get('/mission/suggestions')).data,
  getFeed: async () => (await apiClient.get('/mission/feed')).data,
};
