import { apiClient } from '@/lib/api/client';
import * as RuntimeTypes from '@/lib/types/runtime';

export const RuntimeRepository = {
  getKernel: async () => (await apiClient.get<RuntimeTypes.Kernel>('/runtime/kernel')).data,
  getMemory: async () => (await apiClient.get<RuntimeTypes.Memory>('/runtime/memory')).data,
  getTelemetry: async () => (await apiClient.get<RuntimeTypes.Telemetry>('/runtime/telemetry')).data,
  getProviders: async () => (await apiClient.get<RuntimeTypes.Provider[]>('/runtime/providers')).data,
  getWorkers: async () => (await apiClient.get<RuntimeTypes.Worker[]>('/runtime/workers')).data,
  getQueues: async () => (await apiClient.get<RuntimeTypes.Queue[]>('/runtime/queues')).data,
  getAgents: async () => (await apiClient.get<RuntimeTypes.Agent[]>('/runtime/agents')).data,
  getMetrics: async () => (await apiClient.get<RuntimeTypes.Metrics>('/runtime/metrics')).data,
  getAlerts: async () => (await apiClient.get<RuntimeTypes.Alert[]>('/runtime/alerts')).data,
  getWorkflow: async () => (await apiClient.get<RuntimeTypes.Workflow>('/runtime/workflow')).data,
  getExecutions: async () => (await apiClient.get<RuntimeTypes.Execution[]>('/runtime/executions')).data,
  getRouterDecision: async () => (await apiClient.get<RuntimeTypes.RouterDecision>('/runtime/router-decision')).data,
  getLogs: async () => (await apiClient.get<RuntimeTypes.LogEntry[]>('/runtime/logs')).data,
};
