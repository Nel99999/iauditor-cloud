import React from 'react';
import FAB, { DefaultIcons } from './FAB';

export default {
  title: 'Design System/FAB',
  component: FAB,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Floating Action Button for primary actions. Available in simple and speed dial variants.',
      },
    },
  },
  tags: ['autodocs'],
};

// Simple FAB
export const Simple = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px' }}>
    <p>A simple FAB for single primary actions.</p>
    <FAB
      variant="simple"
      position="bottom-right"
      icon={<DefaultIcons.Plus />}
      label="Create New"
      onClick={() => alert('FAB clicked!')}
    />
  </div>
);

// All Positions
export const Positions = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <h3 style={{ fontSize: '18px', fontWeight: '600' }}>FAB Positions</h3>
    <p>Bottom Right (default)</p>
    <FAB
      variant="simple"
      position="bottom-right"
      icon={<DefaultIcons.Plus />}
      label="Bottom Right"
      onClick={() => alert('Bottom Right')}
    />
  </div>
);

export const PositionCenter = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px' }}>
    <p>Bottom Center</p>
    <FAB
      variant="simple"
      position="bottom-center"
      icon={<DefaultIcons.Plus />}
      label="Bottom Center"
      onClick={() => alert('Bottom Center')}
    />
  </div>
);

export const PositionLeft = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px' }}>
    <p>Bottom Left</p>
    <FAB
      variant="simple"
      position="bottom-left"
      icon={<DefaultIcons.Plus />}
      label="Bottom Left"
      onClick={() => alert('Bottom Left')}
    />
  </div>
);

// Color Variants
export const ColorVariants = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Color Variants</h3>
    <div style={{ display: 'flex', gap: '80px', marginTop: '40px' }}>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Primary</p>
        <FAB
          variant="simple"
          color="primary"
          icon={<DefaultIcons.Plus />}
          label="Primary"
        />
      </div>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Secondary</p>
        <FAB
          variant="simple"
          color="secondary"
          icon={<DefaultIcons.Plus />}
          label="Secondary"
        />
      </div>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Success</p>
        <FAB
          variant="simple"
          color="success"
          icon={<DefaultIcons.Plus />}
          label="Success"
        />
      </div>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Danger</p>
        <FAB
          variant="simple"
          color="danger"
          icon={<DefaultIcons.Plus />}
          label="Danger"
        />
      </div>
    </div>
  </div>
);

// Speed Dial
export const SpeedDial = () => (
  <div style={{ height: '500px', position: 'relative', background: '#f3f4f6', padding: '20px' }}>
    <p>Click the FAB to reveal multiple actions.</p>
    <FAB
      variant="speedDial"
      position="bottom-right"
      icon={<DefaultIcons.Plus />}
      label="Quick Actions"
      actions={[
        {
          icon: <DefaultIcons.Task />,
          label: 'New Task',
          onClick: () => alert('New Task'),
          color: 'primary',
        },
        {
          icon: <DefaultIcons.Inspection />,
          label: 'New Inspection',
          onClick: () => alert('New Inspection'),
          color: 'secondary',
        },
        {
          icon: <DefaultIcons.Checklist />,
          label: 'New Checklist',
          onClick: () => alert('New Checklist'),
          color: 'success',
        },
      ]}
    />
  </div>
);

// Speed Dial with Many Actions
export const SpeedDialManyActions = () => (
  <div style={{ height: '600px', position: 'relative', background: '#f3f4f6', padding: '20px' }}>
    <p>Speed dial with multiple actions.</p>
    <FAB
      variant="speedDial"
      position="bottom-right"
      icon={<DefaultIcons.Plus />}
      label="Create..."
      actions={[
        {
          icon: <DefaultIcons.Task />,
          label: 'Task',
          onClick: () => alert('Task'),
          color: 'primary',
        },
        {
          icon: <DefaultIcons.Inspection />,
          label: 'Inspection',
          onClick: () => alert('Inspection'),
          color: 'primary',
        },
        {
          icon: <DefaultIcons.Checklist />,
          label: 'Checklist',
          onClick: () => alert('Checklist'),
          color: 'primary',
        },
        {
          icon: <DefaultIcons.Edit />,
          label: 'Document',
          onClick: () => alert('Document'),
          color: 'secondary',
        },
        {
          icon: <DefaultIcons.Plus />,
          label: 'Note',
          onClick: () => alert('Note'),
          color: 'success',
        },
      ]}
    />
  </div>
);

// Size Variants
export const Sizes = () => (
  <div style={{ height: '400px', position: 'relative', background: '#f3f4f6', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Size Variants</h3>
    <div style={{ display: 'flex', gap: '100px', marginTop: '40px', alignItems: 'flex-end' }}>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Default (56px)</p>
        <FAB
          variant="simple"
          size="default"
          icon={<DefaultIcons.Plus />}
          label="Default"
        />
      </div>
      <div>
        <p style={{ marginBottom: '60px', fontWeight: '500' }}>Large (64px)</p>
        <FAB
          variant="simple"
          size="large"
          icon={<DefaultIcons.Plus />}
          label="Large"
        />
      </div>
    </div>
  </div>
);

// In Context (with content)
export const InContext = () => (
  <div style={{ height: '600px', position: 'relative', background: '#f3f4f6', padding: '40px' }}>
    <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Tasks</h1>
    
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5'].map((task) => (
        <div
          key={task}
          style={{
            padding: '16px',
            background: 'white',
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          }}
        >
          <h3 style={{ fontWeight: '600', marginBottom: '8px' }}>{task}</h3>
          <p style={{ fontSize: '14px', color: '#6b7280' }}>Task description goes here...</p>
        </div>
      ))}
    </div>

    <FAB
      variant="speedDial"
      position="bottom-right"
      icon={<DefaultIcons.Plus />}
      label="Quick Actions"
      actions={[
        {
          icon: <DefaultIcons.Task />,
          label: 'New Task',
          onClick: () => alert('New Task'),
          color: 'primary',
        },
        {
          icon: <DefaultIcons.Inspection />,
          label: 'New Inspection',
          onClick: () => alert('New Inspection'),
          color: 'secondary',
        },
      ]}
    />
  </div>
);
