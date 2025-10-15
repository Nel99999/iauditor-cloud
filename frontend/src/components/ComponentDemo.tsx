import React from 'react';
import { BottomSheet, useBottomSheet, FAB, FABIcons, Button, Card, GlassCard, Input } from '@/design-system/components';
import { Plus, Mail, Settings, User, Bell } from 'lucide-react';
import './ComponentDemo.css';

const ComponentDemo: React.FC = () => {
  const { isOpen: isSheet1Open, open: openSheet1, close: closeSheet1 } = useBottomSheet();
  const { isOpen: isSheet2Open, open: openSheet2, close: closeSheet2 } = useBottomSheet();
  const { isOpen: isSheet3Open, open: openSheet3, close: closeSheet3 } = useBottomSheet();

  return (
    <div className="component-demo">
      {/* Header */}
      <header className="demo-header">
        <div className="demo-header-content">
          <h1>v2.0 Component Showcase</h1>
          <p>Interactive demo of new BottomSheet and FAB components</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="demo-main">
        {/* Section 1: Bottom Sheets */}
        <section className="demo-section">
          <h2>Bottom Sheets</h2>
          <p className="demo-description">
            Mobile-optimized modals with gesture support. Swipe down to close, swipe up to expand.
          </p>

          <div className="demo-grid">
            <Card padding="lg">
              <h3>Peek Mode (25%)</h3>
              <p>Quick preview or notification</p>
              <Button variant="primary" onClick={() => openSheet1('peek')}>
                Open Peek Sheet
              </Button>
            </Card>

            <Card padding="lg">
              <h3>Half Mode (50%)</h3>
              <p>Default for most content</p>
              <Button variant="secondary" onClick={() => openSheet2('half')}>
                Open Half Sheet
              </Button>
            </Card>

            <Card padding="lg">
              <h3>Full Mode (90%)</h3>
              <p>Forms or detailed content</p>
              <Button variant="primary" onClick={() => openSheet3('full')}>
                Open Full Sheet
              </Button>
            </Card>
          </div>
        </section>

        {/* Section 2: FAB Components */}
        <section className="demo-section">
          <h2>Floating Action Buttons (FAB)</h2>
          <p className="demo-description">
            Primary action buttons that float above content. Try the speed dial for multiple actions.
          </p>

          <div className="demo-grid">
            <Card padding="lg">
              <h3>Simple FAB</h3>
              <p>Single primary action</p>
              <div style={{ position: 'relative', height: '200px', background: '#f3f4f6', borderRadius: '8px', marginTop: '16px' }}>
                <p style={{ padding: '20px', fontSize: '14px', color: '#6b7280' }}>
                  Content area with FAB in bottom-right
                </p>
                <FAB
                  variant="simple"
                  position="bottom-right"
                  icon={<FABIcons.Plus />}
                  onClick={() => alert('Simple FAB clicked!')}
                  color="primary"
                />
              </div>
            </Card>

            <Card padding="lg">
              <h3>Speed Dial FAB</h3>
              <p>Multiple related actions</p>
              <div style={{ position: 'relative', height: '200px', background: '#f3f4f6', borderRadius: '8px', marginTop: '16px' }}>
                <p style={{ padding: '20px', fontSize: '14px', color: '#6b7280' }}>
                  Click FAB to reveal actions
                </p>
                <FAB
                  variant="speedDial"
                  position="bottom-right"
                  icon={<FABIcons.Plus />}
                  actions={[
                    { icon: <FABIcons.Task />, label: 'New Task', onClick: () => alert('Task!'), color: 'primary' },
                    { icon: <FABIcons.Inspection />, label: 'Inspection', onClick: () => alert('Inspection!'), color: 'secondary' },
                    { icon: <FABIcons.Checklist />, label: 'Checklist', onClick: () => alert('Checklist!'), color: 'success' },
                  ]}
                />
              </div>
            </Card>
          </div>
        </section>

        {/* Section 3: Design System Components */}
        <section className="demo-section">
          <h2>Design System Components</h2>
          <p className="demo-description">
            Modern, token-driven components with glassmorphism effects.
          </p>

          <div className="demo-grid">
            <GlassCard hover padding="lg">
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <User size={24} color="#3b82f6" />
                </div>
                <div>
                  <h3>Glass Card</h3>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>With hover effect</p>
                </div>
              </div>
              <p style={{ fontSize: '14px', lineHeight: '1.6' }}>
                Glassmorphism design with backdrop blur and transparency.
              </p>
            </GlassCard>

            <Card padding="lg">
              <h3>Input Components</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
                <Input icon={<Mail size={18} />} placeholder="Email address" />
                <Input icon={<User size={18} />} placeholder="Full name" />
              </div>
            </Card>

            <Card padding="lg">
              <h3>Button Variants</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                <Button variant="primary" size="sm">Primary</Button>
                <Button variant="secondary" size="sm">Secondary</Button>
                <Button variant="ghost" size="sm">Ghost</Button>
                <Button variant="danger" size="sm">Danger</Button>
              </div>
            </Card>
          </div>
        </section>

        {/* Section 4: Mobile Preview */}
        <section className="demo-section">
          <h2>Mobile Optimized</h2>
          <p className="demo-description">
            All components are touch-optimized with ≥44px touch targets and gesture support.
          </p>

          <Card padding="lg">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <h3>✓ Touch Targets ≥44px</h3>
                <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>All interactive elements meet minimum size</p>
                
                <h3>✓ Gesture Support</h3>
                <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Swipe to open/close/expand</p>
                
                <h3>✓ Adaptive Navigation</h3>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>Bottom nav → Nav rail → Sidebar</p>
              </div>
            </div>
          </Card>
        </section>

        {/* Documentation Section */}
        <section className="demo-section">
          <h2>Documentation</h2>
          <div className="demo-grid">
            <Card padding="lg">
              <h3>📚 20,000+ Words</h3>
              <p>Comprehensive guides covering:</p>
              <ul style={{ fontSize: '14px', lineHeight: '1.8', paddingLeft: '20px' }}>
                <li>Design System Guide</li>
                <li>Component API Reference</li>
                <li>Mobile UX Best Practices</li>
                <li>Testing Strategies</li>
                <li>TypeScript Migration</li>
              </ul>
            </Card>

            <Card padding="lg">
              <h3>🎨 Storybook</h3>
              <p>40+ interactive component stories</p>
              <pre style={{ background: '#f3f4f6', padding: '12px', borderRadius: '4px', fontSize: '12px', marginTop: '12px' }}>
                cd /app/frontend{'\n'}
                yarn storybook{'\n'}
                # Open localhost:6006
              </pre>
            </Card>

            <Card padding="lg">
              <h3>🧪 Visual Testing</h3>
              <p>Playwright visual regression tests</p>
              <pre style={{ background: '#f3f4f6', padding: '12px', borderRadius: '4px', fontSize: '12px', marginTop: '12px' }}>
                cd /app/frontend{'\n'}
                yarn test:visual
              </pre>
            </Card>
          </div>
        </section>
      </main>

      {/* Bottom Sheets */}
      <BottomSheet isOpen={isSheet1Open} onClose={closeSheet1} snapPoint="peek" title="Peek Mode">
        <div style={{ padding: '0 0 20px 0' }}>
          <p style={{ marginBottom: '16px' }}>This is a peek sheet at 25% height.</p>
          <p>Swipe up to expand or swipe down to close.</p>
        </div>
      </BottomSheet>

      <BottomSheet isOpen={isSheet2Open} onClose={closeSheet2} snapPoint="half" title="Half Mode">
        <div>
          <p style={{ marginBottom: '16px' }}>This is a half-height sheet (50%).</p>
          <p style={{ marginBottom: '16px' }}>Perfect for most content like task details, filters, or quick forms.</p>
          
          <h4 style={{ marginTop: '24px', marginBottom: '12px' }}>Example Content</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <Input placeholder="Task title" />
            <Input placeholder="Description" />
            <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
              <Button variant="primary" fullWidth>Save</Button>
              <Button variant="secondary" fullWidth onClick={closeSheet2}>Cancel</Button>
            </div>
          </div>
        </div>
      </BottomSheet>

      <BottomSheet isOpen={isSheet3Open} onClose={closeSheet3} snapPoint="full" title="Full Screen Mode">
        <div>
          <p style={{ marginBottom: '16px' }}>This is a full-screen sheet at 90% height.</p>
          <p style={{ marginBottom: '16px' }}>Ideal for forms, detailed content, or multi-step flows.</p>
          
          <h4 style={{ marginTop: '24px', marginBottom: '12px' }}>Features:</h4>
          <ul style={{ paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>Swipe down to close</li>
            <li>Tap backdrop to dismiss</li>
            <li>Press ESC key to close</li>
            <li>Body scroll locked</li>
            <li>Smooth spring animations</li>
            <li>Full accessibility support</li>
          </ul>

          <h4 style={{ marginTop: '24px', marginBottom: '12px' }}>Try scrolling:</h4>
          {Array.from({ length: 10 }).map((_, i) => (
            <p key={i} style={{ padding: '12px', background: 'rgba(0,0,0,0.02)', borderRadius: '4px', marginBottom: '8px' }}>
              Scrollable content item {i + 1}
            </p>
          ))}
        </div>
      </BottomSheet>

      {/* Page-level FAB for demo */}
      <FAB
        variant="speedDial"
        position="bottom-right"
        icon={<Plus size={24} />}
        color="primary"
        actions={[
          { icon: <Settings size={20} />, label: 'Settings', onClick: () => alert('Settings'), color: 'secondary' },
          { icon: <Bell size={20} />, label: 'Notifications', onClick: () => alert('Notifications'), color: 'info' },
          { icon: <User size={20} />, label: 'Profile', onClick: () => alert('Profile'), color: 'success' },
        ]}
      />
    </div>
  );
};

export default ComponentDemo;
