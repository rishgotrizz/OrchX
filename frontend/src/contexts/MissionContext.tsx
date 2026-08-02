"use client";

import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MissionRepository } from '@/lib/repositories/MissionRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';

export interface MissionState {
  telemetry: any;
  workflow: any;
  tasks: any;
  sessions: any;
  activity: any;
  credits: any;
  suggestions: any;
  feed: any;
  isLoading: boolean;
  error: Error | null;
}

const MissionContext = createContext<MissionState | undefined>(undefined);

export function MissionProvider({ children }: { children: ReactNode }) {
  const { data: telemetry, isLoading: l1, error: e1 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'telemetry'], queryFn: MissionRepository.getTelemetry });
  const { data: workflow, isLoading: l2, error: e2 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'workflow'], queryFn: MissionRepository.getWorkflow });
  const { data: tasks, isLoading: l3, error: e3 } = useQuery({ queryKey: [...QueryKeys.mission.tasks], queryFn: MissionRepository.getTasks });
  const { data: sessions, isLoading: l4, error: e4 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'sessions'], queryFn: MissionRepository.getSessions });
  const { data: activity, isLoading: l5, error: e5 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'activity'], queryFn: MissionRepository.getActivity });
  const { data: credits, isLoading: l6, error: e6 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'credits'], queryFn: MissionRepository.getCredits });
  const { data: suggestions, isLoading: l7, error: e7 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'suggestions'], queryFn: MissionRepository.getSuggestions });
  const { data: feed, isLoading: l8, error: e8 } = useQuery({ queryKey: [...QueryKeys.mission.workflows, 'feed'], queryFn: MissionRepository.getFeed });

  const isLoading = l1 || l2 || l3 || l4 || l5 || l6 || l7 || l8;
  const error = e1 || e2 || e3 || e4 || e5 || e6 || e7 || e8 || null;

  const state: MissionState = {
    telemetry,
    workflow,
    tasks,
    sessions,
    activity,
    credits,
    suggestions,
    feed,
    isLoading,
    error: error as Error | null,
  };

  return (
    <MissionContext.Provider value={state}>
      {children}
    </MissionContext.Provider>
  );
}

export function useMissionContext() {
  const context = useContext(MissionContext);
  if (!context) throw new Error('useMissionContext must be used within a MissionProvider');
  return context;
}
