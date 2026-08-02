"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import * as PreviewTypes from '@/lib/types/preview';
import { PreviewRepository } from '@/lib/repositories/PreviewRepository';
import { QueryKeys } from '@/lib/repositories/QueryKeys';

export interface PreviewState {
  artifacts: PreviewTypes.Artifact[];
  session: PreviewTypes.PreviewSession;
  setSession: React.Dispatch<React.SetStateAction<PreviewTypes.PreviewSession>>;
  isLoading: boolean;
  error: Error | null;
}

const PreviewContext = createContext<PreviewState | undefined>(undefined);

export function PreviewProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<PreviewTypes.PreviewSession>({
    artifactId: 'art-1', // Default selected
    version: null,
    deviceProfile: 'responsive',
    zoom: 1,
    fullscreen: false,
    compareMode: false,
    rendererMode: 'preview',
    compareArtifactId: null,
  });

  const { data: artifacts = [], isLoading, error } = useQuery({
    queryKey: QueryKeys.preview.artifacts,
    queryFn: PreviewRepository.getArtifacts,
  });

  const state: PreviewState = {
    artifacts,
    session,
    setSession,
    isLoading,
    error: error as Error | null,
  };

  return (
    <PreviewContext.Provider value={state}>
      {children}
    </PreviewContext.Provider>
  );
}

export function usePreviewContext() {
  const context = useContext(PreviewContext);
  if (!context) {
    throw new Error('usePreviewContext must be used within a PreviewProvider');
  }
  return context;
}
