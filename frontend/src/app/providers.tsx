"use client";

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React, { useState, useEffect } from 'react';

import { ExperienceProvider } from '@/contexts/ExperienceContext';
import { SettingsProvider } from '@/contexts/SettingsContext';

// Initialize all registries once at module load time (client-side).
// This guarantees that no matter which route is visited first, all
// settings categories, configurations, and widget registrations are
// available before any component tries to read from them.
let _registriesInitialized = false;

function ensureRegistriesInitialized() {
  if (_registriesInitialized) return;
  _registriesInitialized = true;
  // Lazy-import to avoid SSR issues — these are client-only registries.
  import('@/components/widgets/settings').then(({ initializeSettingsWidgets, initializeSettingsMockData }) => {
    initializeSettingsWidgets();
    initializeSettingsMockData();
  });
}

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60, // 1 minute
        refetchOnWindowFocus: false,
        // Gracefully handle 404s from missing backend routes — don't crash
        retry: (failureCount, error: any) => {
          if (error?.response?.status === 404) return false;
          return failureCount < 1;
        }
      },
    },
  }));

  const [mswReady, setMswReady] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Initialize all registries before any page renders
      ensureRegistriesInitialized();

      console.log(`OrchX Booted. Commit: ${process.env.NEXT_PUBLIC_BUILD_COMMIT_SHA || "UNKNOWN"}`);
      if (process.env.NEXT_PUBLIC_ENABLE_MSW !== 'false') {
        import('@/lib/mocks/browser')
          .then(async ({ worker }) => {
            await worker.start({ onUnhandledRequest: 'bypass' });
            setMswReady(true);
          })
          .catch(() => {
            // MSW failed to register (service worker not present or blocked).
            // Fall through so the app still renders — backend routes will be used.
            setMswReady(true);
          });
      } else {
        setMswReady(true);
      }
    }
  }, []);

  if (!mswReady) {
    return <div className="h-screen w-screen bg-void flex items-center justify-center text-text-muted">Initializing Runtime...</div>;
  }

  return (
    <ExperienceProvider>
      <QueryClientProvider client={queryClient}>
        <SettingsProvider>
          {children}
        </SettingsProvider>
      </QueryClientProvider>
    </ExperienceProvider>
  );
}
