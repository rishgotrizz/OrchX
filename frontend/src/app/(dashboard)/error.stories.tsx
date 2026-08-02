import type { Meta, StoryObj } from '@storybook/react';
import DashboardError from '@/app/(dashboard)/error';

const meta = {
  title: 'States/ErrorBoundary',
  component: DashboardError,
  parameters: { layout: 'fullscreen' },
} satisfies Meta<typeof DashboardError>;

export default meta;
type Story = StoryObj<typeof meta>;

export const KernelException: Story = {
  args: {
    error: Object.assign(new Error("Connection to AI orchestration agent timed out after 30000ms."), { digest: "ERR-948A7B" }),
    reset: () => console.log('Reset triggered')
  }
};
