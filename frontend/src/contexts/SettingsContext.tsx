"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { SettingsSession } from '@/lib/types/settings';
import { getAllConfigurations } from '@/lib/settings-registry';
import { SettingsRepository } from '@/lib/repositories/SettingsRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';

export interface SettingsState {
  session: SettingsSession;
  setSession: React.Dispatch<React.SetStateAction<SettingsSession>>;
  getSettingValue: (configId: string) => any;
  updateSettingValue: (configId: string, value: any, persist?: boolean) => void;
}

const SettingsContext = createContext<SettingsState | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<SettingsSession>({
    currentCategory: 'appearance',
    currentProfile: 'default',
    searchQuery: '',
    modifiedSettings: {}
  });

  const { data: persistedSettings = {} } = useQuery({
    queryKey: QueryKeys.settings.all,
    queryFn: SettingsRepository.getGlobalProfile
  });

  const updateMutation = useMutation({
    mutationFn: (newSettings: Record<string, any>) => SettingsRepository.updateGlobalProfile(newSettings),
    onMutate: async (newSettings) => {
      await queryClient.cancelQueries({ queryKey: QueryKeys.settings.all });
      const previousSettings = queryClient.getQueryData<Record<string, any>>(QueryKeys.settings.all);
      queryClient.setQueryData<Record<string, any>>(QueryKeys.settings.all, old => ({ ...old, ...newSettings }));
      return { previousSettings };
    },
    onError: (err, newSettings, context) => {
      if (context?.previousSettings) {
        queryClient.setQueryData(QueryKeys.settings.all, context.previousSettings);
      }
    }
  });

  const getSettingValue = (configId: string) => {
    if (session.modifiedSettings[configId] !== undefined) return session.modifiedSettings[configId];
    if (persistedSettings[configId] !== undefined) return persistedSettings[configId];
    const config = getAllConfigurations().find(c => c.id === configId);
    return config?.defaultValue;
  };

  const updateSettingValue = (configId: string, value: any, persist: boolean = false) => {
    if (persist) {
      updateMutation.mutate({ [configId]: value });
      
      const newModified = { ...session.modifiedSettings };
      delete newModified[configId];
      setSession(s => ({ ...s, modifiedSettings: newModified }));
    } else {
      setSession(s => ({ ...s, modifiedSettings: { ...s.modifiedSettings, [configId]: value } }));
    }
  };

  return (
    <SettingsContext.Provider value={{ session, setSession, getSettingValue, updateSettingValue }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettingsContext() {
  const context = useContext(SettingsContext);
  if (!context) throw new Error('useSettingsContext must be used within a SettingsProvider');
  return context;
}
