import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './Badge';

const meta = {
  title: 'Core/Badge',
  component: Badge,
  parameters: { layout: 'centered' },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { children: 'Default Badge' } };
export const Healthy: Story = { args: { variant: 'healthy', children: 'Online' } };
export const Warning: Story = { args: { variant: 'warning', children: 'Degraded' } };
export const ErrorBadge: Story = { args: { variant: 'error', children: 'Failed' } };
