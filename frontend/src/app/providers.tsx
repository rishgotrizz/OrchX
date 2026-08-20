"use client";

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React, { useState, useEffect } from 'react';

import { ExperienceProvider } from '@/contexts/ExperienceContext';
import { SettingsProvider } from '@/contexts/SettingsContext';

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60, // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  }));

  const [mswReady, setMswReady] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (process.env.NEXT_PUBLIC_ENABLE_MSW !== 'false') {
        import('@/lib/mocks/browser')
          .then(async ({ worker }) => {
            await worker.start({ onUnhandledRequest: 'bypass' });
            setMswReady(true);
          })
          .catch(() => {
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
