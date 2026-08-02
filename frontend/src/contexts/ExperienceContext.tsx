"use client";

import React, { createContext, useContext, ReactNode, useEffect, useState } from 'react';
import { eventBus } from '@/lib/event-bus';

export type PerformanceMode = 'ultra' | 'high' | 'medium' | 'low' | 'battery-saver';
export type ExperienceProfile = 'minimal' | 'professional' | 'immersive' | 'developer';

export interface ExperienceState {
  performanceMode: PerformanceMode;
  profile: ExperienceProfile;
  reducedMotion: boolean;
  setPerformanceMode: (mode: PerformanceMode) => void;
  setProfile: (profile: ExperienceProfile) => void;
}

const ExperienceContext = createContext<ExperienceState | undefined>(undefined);

export function ExperienceProvider({ children }: { children: ReactNode }) {
  const [reducedMotion, setReducedMotion] = useState(false);
  const [performanceMode, setPerformanceMode] = useState<PerformanceMode>('high');
  const [profile, setProfile] = useState<ExperienceProfile>('professional');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // OS Level Accessibility Override
      const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
      const updateMotion = (e: MediaQueryListEvent | MediaQueryList) => {
        setReducedMotion(e.matches);
        if (e.matches) {
          eventBus.emit('ReducedMotionEnabled');
          setPerformanceMode('battery-saver');
        }
      };
      
      updateMotion(mql);
      mql.addEventListener('change', updateMotion);
      return () => mql.removeEventListener('change', updateMotion);
    }
  }, []);

  const state = { performanceMode, profile, reducedMotion, setPerformanceMode, setProfile };

  return (
    <ExperienceContext.Provider value={state}>
      {children}
    </ExperienceContext.Provider>
  );
}

export function useExperienceContext() {
  const context = useContext(ExperienceContext);
  if (!context) throw new Error('useExperienceContext must be used within an ExperienceProvider');
  return context;
}
