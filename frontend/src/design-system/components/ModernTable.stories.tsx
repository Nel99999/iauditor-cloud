// @ts-nocheck
import React from 'react';
import ModernTable from './ModernTable';

export default {
  title: 'Design System/ModernTable',
  component: ModernTable,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

const sampleData = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive' },
  { id: 4, name: 'Alice Williams', email: 'alice@example.com', role: 'Manager', status: 'Active' },
  { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', role: 'User', status: 'Active' },
];

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'role', label: 'Role' },
  { key: 'status', label: 'Status' },
];

export const Default = () => (
  <ModernTable data={sampleData} columns={columns} />
);

export const WithActions = () => (
  <ModernTable
    data={sampleData}
    columns={columns}
    onRowClick={(row) => alert(`Clicked row: ${row.name}`)}
  />
);

export const Empty = () => (
  <ModernTable data={[]} columns={columns} />
);
