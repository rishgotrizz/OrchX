import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Core/Button',
  component: Button,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { children: 'Default Button' } };
export const Primary: Story = { args: { variant: 'primary', children: 'Primary Action' } };
export const Ghost: Story = { args: { variant: 'ghost', children: 'Ghost Button' } };
export const Link: Story = { args: { variant: 'link', children: 'Link Button' } };
export const Loading: Story = { args: { isLoading: true, children: 'Executing Task' } };
