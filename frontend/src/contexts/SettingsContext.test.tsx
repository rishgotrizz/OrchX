import React from 'react';
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SettingsProvider, useSettingsContext } from './SettingsContext';
import DashboardError from '@/app/(dashboard)/error';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { initializeSettingsMockData } from '@/components/widgets/settings';

// Mock useRouter from next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe('SettingsContext', () => {
  beforeAll(() => {
    initializeSettingsMockData();
  });

  // Test helper component
  function TestConsumer() {
    const { getSettingValue } = useSettingsContext();
    const theme = getSettingValue('appearance.theme');
    return <div data-testid="theme-val">{theme}</div>;
  }

  it('throws error when rendered outside SettingsProvider', () => {
    // Suppress console.error output for the intentional error throw
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => render(<TestConsumer />)).toThrow(
      'useSettingsContext must be used within a SettingsProvider'
    );
    
    consoleErrorSpy.mockRestore();
  });

  it('provides configuration state when rendered inside SettingsProvider', () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    
    render(
      <QueryClientProvider client={queryClient}>
        <SettingsProvider>
          <TestConsumer />
        </SettingsProvider>
      </QueryClientProvider>
    );
    
    // The default theme value is 'dark'.
    expect(screen.getByTestId('theme-val').textContent).toBe('dark');
  });

  it('allows emergency DashboardError to render without any SettingsProvider context', () => {
    const mockError = new Error('Test crash');
    const mockReset = vi.fn();
    
    render(
      <DashboardError error={mockError} reset={mockReset} />
    );
    
    expect(screen.getByText('Kernel Exception')).toBeDefined();
    expect(screen.getByText('Test crash')).toBeDefined();
  });
});
