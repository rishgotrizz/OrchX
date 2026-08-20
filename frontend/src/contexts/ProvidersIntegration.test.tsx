import React from 'react';
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryProvider } from '@/app/providers';
import DashboardLayout from '@/app/(dashboard)/layout';
import MissionControlPage from '@/app/(dashboard)/mission-control/page';
import { initializeSettingsMockData } from '@/components/widgets/settings';

// Mock Next.js navigation hooks
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/mission-control',
}));

describe('Providers Integration & Dashboard Layout Composition', () => {
  beforeAll(() => {
    initializeSettingsMockData();
  });

  it('renders the complete root providers wrapper, dashboard layout, and Mission Control page without throwing context exceptions', async () => {
    const { container } = render(
      <ReactQueryProvider>
        <DashboardLayout>
          <MissionControlPage />
        </DashboardLayout>
      </ReactQueryProvider>
    );

    // Initial render is the loading state "Initializing Runtime..."
    expect(screen.getByText('Initializing Runtime...')).toBeDefined();
  });

  it('renders MissionControlPage safely with default context values even without SettingsProvider', () => {
    // Context now has a safe default — no throw from useSettingsContext.
    // MissionControlPage still needs QueryClientProvider for its own useQuery calls.
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    expect(() =>
      render(
        <QueryClientProvider client={qc}>
          <MissionControlPage />
        </QueryClientProvider>
      )
    ).not.toThrow();
  });
});
