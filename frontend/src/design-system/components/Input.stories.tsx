// @ts-nocheck
import Input from './Input';
import { Mail, Lock, Search, User } from 'lucide-react';

export default {
  title: 'Design System/Input',
  component: Input,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export const Default = () => <Input placeholder="Enter text..." />;

export const Sizes = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
    <Input size="sm" placeholder="Small input" />
    <Input size="md" placeholder="Medium input (default)" />
    <Input size="lg" placeholder="Large input" />
  </div>
);

export const WithIcons = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
    <Input icon={<Mail size={18} />} placeholder="Email" type="email" />
    <Input icon={<Lock size={18} />} placeholder="Password" type="password" />
    <Input icon={<Search size={18} />} placeholder="Search..." />
    <Input icon={<User size={18} />} placeholder="Username" />
  </div>
);

export const States = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
    <Input placeholder="Normal" />
    <Input placeholder="Disabled" disabled />
    <Input placeholder="Read only" readOnly value="Read only value" />
    <Input placeholder="With error" error />
  </div>
);

export const Types = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
    <Input type="text" placeholder="Text" />
    <Input type="email" placeholder="Email" />
    <Input type="password" placeholder="Password" />
    <Input type="number" placeholder="Number" />
    <Input type="tel" placeholder="Phone" />
    <Input type="url" placeholder="URL" />
    <Input type="date" />
  </div>
);
