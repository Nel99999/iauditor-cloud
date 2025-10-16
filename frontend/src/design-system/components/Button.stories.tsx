import Button from './Button';
import { Plus, Save, Trash2, Download } from 'lucide-react';

export default {
  title: 'Design System/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants, sizes, and states.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger'],
      description: 'Button style variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Button size',
    },
    disabled: {
      control: 'boolean',
      description: 'Disabled state',
    },
    loading: {
      control: 'boolean',
      description: 'Loading state',
    },
    fullWidth: {
      control: 'boolean',
      description: 'Full width button',
    },
  },
};

// Default story
export const Default = {
  args: {
    children: 'Button',
    variant: 'primary',
    size: 'md',
  },
};

// All Variants
export const Variants = () => (
  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
    <Button variant="primary">Primary</Button>
    <Button variant="secondary">Secondary</Button>
    <Button variant="ghost">Ghost</Button>
    <Button variant="danger">Danger</Button>
  </div>
);

// All Sizes
export const Sizes = () => (
  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
    <Button size="sm">Small</Button>
    <Button size="md">Medium</Button>
    <Button size="lg">Large</Button>
  </div>
);

// With Icons
export const WithIcons = () => (
  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
    <Button icon={<Plus size={20} />}>Create</Button>
    <Button variant="secondary" icon={<Save size={20} />}>Save</Button>
    <Button variant="ghost" icon={<Download size={20} />}>Download</Button>
    <Button variant="danger" icon={<Trash2 size={20} />}>Delete</Button>
  </div>
);

// Icon Only
export const IconOnly = () => (
  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
    <Button icon={<Plus size={20} />} />
    <Button variant="secondary" icon={<Save size={20} />} />
    <Button variant="ghost" icon={<Download size={20} />} />
    <Button variant="danger" icon={<Trash2 size={20} />} />
  </div>
);

// States
export const States = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <div style={{ display: 'flex', gap: '12px' }}>
      <Button>Normal</Button>
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
    </div>
    <div style={{ display: 'flex', gap: '12px' }}>
      <Button variant="secondary">Normal</Button>
      <Button variant="secondary" disabled>Disabled</Button>
      <Button variant="secondary" loading>Loading</Button>
    </div>
  </div>
);

// Full Width
export const FullWidth = () => (
  <div style={{ width: '300px' }}>
    <Button fullWidth>Full Width Button</Button>
  </div>
);

// Interactive Example
export const Interactive = {
  args: {
    children: 'Click me!',
    variant: 'primary',
    size: 'md',
    onClick: () => alert('Button clicked!'),
  },
};
