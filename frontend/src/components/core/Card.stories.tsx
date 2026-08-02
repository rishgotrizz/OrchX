import type { Meta, StoryObj } from '@storybook/react';
import { Card } from './Card';

const meta = {
  title: 'Core/Card',
  component: Card,
  parameters: { layout: 'centered' },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Card className="p-6 w-96">
      <h3 className="text-lg font-semibold mb-2 text-text-primary">Premium Card</h3>
      <p className="text-sm text-text-secondary">This card features interactive hover elevation, glass borders, and subtle glowing shadows defined in the OrchX design system.</p>
    </Card>
  )
};
