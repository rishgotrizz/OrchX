import type { Meta, StoryObj } from '@storybook/react';
import { EmptyState } from './EmptyState';
import { Activity } from 'lucide-react';
import { Button } from './Button';

const meta = {
  title: 'Core/EmptyState',
  component: EmptyState,
  parameters: { layout: 'centered' },
} satisfies Meta<typeof EmptyState>;

export default meta;
type Story = StoryObj<typeof meta>;

export const WithAction: Story = {
  args: {
    icon: Activity,
    title: 'No active orchestration',
    description: 'Begin by creating your first mission. Agent task activity will stream here.',
    action: <Button variant="primary">Create Mission</Button>
  }
};
