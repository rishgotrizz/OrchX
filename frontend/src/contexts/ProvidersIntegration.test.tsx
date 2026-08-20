import React from 'react';
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
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

  it('fails with settings context exception if Mission Control is rendered directly without ReactQueryProvider', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => render(<MissionControlPage />)).toThrow(
      /useSettingsContext must be used within a SettingsProvider/
    );
    
    consoleErrorSpy.mockRestore();
  });
});
