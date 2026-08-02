"use client";

import React from 'react';
import { useExperienceContext } from '@/contexts/ExperienceContext';

export function BackgroundManager() {
  const { reducedMotion, profile, performanceMode } = useExperienceContext();

  if (reducedMotion || performanceMode === 'battery-saver') {
    return <div className="fixed inset-0 bg-void -z-50 pointer-events-none" />;
  }

  if (profile === 'minimal') {
    return <div className="fixed inset-0 bg-gradient-to-br from-void to-surface -z-50 pointer-events-none" />;
  }

  return (
    <div className="fixed inset-0 -z-50 pointer-events-none overflow-hidden bg-void">
      {/* Fallback CSS animated background simulating a mesh gradient/aurora */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-accent-primary opacity-10 blur-[120px] animate-pulse" style={{ animationDuration: '8s' }} />
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-accent-secondary opacity-10 blur-[150px] animate-pulse" style={{ animationDuration: '12s', animationDelay: '2s' }} />
      <div className="absolute top-[40%] left-[30%] w-[40%] h-[40%] bg-[#00E676] opacity-5 blur-[100px] animate-pulse" style={{ animationDuration: '10s', animationDelay: '4s' }} />
    </div>
  );
}
