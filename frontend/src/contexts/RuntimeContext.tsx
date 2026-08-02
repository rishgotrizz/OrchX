"use client";

import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import * as RuntimeTypes from '@/lib/types/runtime';
import { RuntimeRepository } from '@/lib/repositories/RuntimeRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';

export interface RuntimeState {
  kernel: RuntimeTypes.Kernel | undefined;
  memory: RuntimeTypes.Memory | undefined;
  telemetry: RuntimeTypes.Telemetry | undefined;
  providers: RuntimeTypes.Provider[] | undefined;
  workers: RuntimeTypes.Worker[] | undefined;
  queues: RuntimeTypes.Queue[] | undefined;
  agents: RuntimeTypes.Agent[] | undefined;
  metrics: RuntimeTypes.Metrics | undefined;
  alerts: RuntimeTypes.Alert[] | undefined;
  workflow: RuntimeTypes.Workflow | undefined;
  executions: RuntimeTypes.Execution[] | undefined;
  routerDecision: RuntimeTypes.RouterDecision | undefined;
  logs: RuntimeTypes.LogEntry[] | undefined;
  isLoading: boolean;
  error: Error | null;
}

const RuntimeContext = createContext<RuntimeState | undefined>(undefined);

export function RuntimeProvider({ children }: { children: ReactNode }) {
  const { data: kernel, isLoading: l1 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'kernel'], queryFn: RuntimeRepository.getKernel });
  const { data: memory, isLoading: l2 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'memory'], queryFn: RuntimeRepository.getMemory });
  const { data: telemetry, isLoading: l3 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'telemetry'], queryFn: RuntimeRepository.getTelemetry });
  const { data: providers, isLoading: l4 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'providers'], queryFn: RuntimeRepository.getProviders });
  const { data: workers, isLoading: l5 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'workers'], queryFn: RuntimeRepository.getWorkers });
  const { data: queues, isLoading: l6 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'queues'], queryFn: RuntimeRepository.getQueues });
  const { data: agents, isLoading: l7 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'agents'], queryFn: RuntimeRepository.getAgents });
  const { data: metrics, isLoading: l8 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'metrics'], queryFn: RuntimeRepository.getMetrics });
  const { data: alerts, isLoading: l9 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'alerts'], queryFn: RuntimeRepository.getAlerts });
  const { data: workflow, isLoading: l10 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'workflow'], queryFn: RuntimeRepository.getWorkflow });
  const { data: executions, isLoading: l11 } = useQuery({ queryKey: [...QueryKeys.runtime.executions], queryFn: RuntimeRepository.getExecutions });
  const { data: routerDecision, isLoading: l12 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'router-decision'], queryFn: RuntimeRepository.getRouterDecision });
  const { data: logs, isLoading: l13 } = useQuery({ queryKey: [...QueryKeys.runtime.metrics, 'logs'], queryFn: RuntimeRepository.getLogs });

  const isLoading = l1 || l2 || l3 || l4 || l5 || l6 || l7 || l8 || l9 || l10 || l11 || l12 || l13;

  const state: RuntimeState = {
    kernel,
    memory,
    telemetry,
    providers,
    workers,
    queues,
    agents,
    metrics,
    alerts,
    workflow,
    executions,
    routerDecision,
    logs,
    isLoading,
    error: null, // Error aggregation
  };

  return (
    <RuntimeContext.Provider value={state}>
      {children}
    </RuntimeContext.Provider>
  );
}

export function useRuntimeContext() {
  const context = useContext(RuntimeContext);
  if (!context) throw new Error('useRuntimeContext must be used within a RuntimeProvider');
  return context;
}
