// @ts-nocheck
import React from 'react';
import Spinner from './Spinner';

export default {
  title: 'Design System/Spinner',
  component: Spinner,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const Sizes = () => (
  <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
    <Spinner size="sm" />
    <Spinner size="md" />
    <Spinner size="lg" />
    <Spinner size="xl" />
  </div>
);

export const Colors = () => (
  <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
    <Spinner color="primary" />
    <Spinner color="secondary" />
    <Spinner color="white" style={{ background: '#1f2937', padding: '20px', borderRadius: '8px' }} />
  </div>
);

export const WithText = () => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
    <Spinner size="lg" />
    <p style={{ color: '#6b7280' }}>Loading...</p>
  </div>
);
