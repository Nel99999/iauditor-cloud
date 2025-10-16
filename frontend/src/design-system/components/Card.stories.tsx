// @ts-nocheck
import Card from './Card';
import GlassCard from './GlassCard';
import Button from './Button';

export default {
  title: 'Design System/Cards',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Card components for grouping content with different visual styles.',
      },
    },
  },
  tags: ['autodocs'],
};

// Basic Card
export const BasicCard = () => (
  <Card>
    <h3 style={{ marginBottom: '12px', fontSize: '18px', fontWeight: '600' }}>Card Title</h3>
    <p style={{ marginBottom: '16px', color: '#6b7280' }}>
      This is a basic card component with default styling.
    </p>
    <Button size="sm">Action</Button>
  </Card>
);

// Card with Padding
export const CardPadding = () => (
  <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
    <Card padding="sm" style={{ width: '250px' }}>
      <h4>Small Padding</h4>
      <p>Less space inside</p>
    </Card>
    <Card padding="md" style={{ width: '250px' }}>
      <h4>Medium Padding</h4>
      <p>Default spacing</p>
    </Card>
    <Card padding="lg" style={{ width: '250px' }}>
      <h4>Large Padding</h4>
      <p>More space inside</p>
    </Card>
  </div>
);

// Glass Card
export const GlassmorphismCard = () => (
  <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px', borderRadius: '12px' }}>
    <GlassCard>
      <h3 style={{ marginBottom: '12px', fontSize: '18px', fontWeight: '600' }}>Glass Card</h3>
      <p style={{ marginBottom: '16px', color: '#6b7280' }}>
        This card has a glassmorphism effect with backdrop blur and transparency.
      </p>
      <Button size="sm" variant="primary">Learn More</Button>
    </GlassCard>
  </div>
);

// Glass Card Variants
export const GlassCardVariants = () => (
  <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px', borderRadius: '12px' }}>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
      <GlassCard hover={false}>
        <h4 style={{ marginBottom: '8px' }}>No Hover</h4>
        <p style={{ fontSize: '14px', color: '#6b7280' }}>Static glass card</p>
      </GlassCard>
      <GlassCard hover>
        <h4 style={{ marginBottom: '8px' }}>With Hover</h4>
        <p style={{ fontSize: '14px', color: '#6b7280' }}>Hover to see effect</p>
      </GlassCard>
      <GlassCard blur="md">
        <h4 style={{ marginBottom: '8px' }}>Medium Blur</h4>
        <p style={{ fontSize: '14px', color: '#6b7280' }}>Less transparency</p>
      </GlassCard>
      <GlassCard blur="xl">
        <h4 style={{ marginBottom: '8px' }}>Extra Blur</h4>
        <p style={{ fontSize: '14px', color: '#6b7280' }}>More transparency</p>
      </GlassCard>
    </div>
  </div>
);

// Stats Cards
export const StatsCards = () => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
    <GlassCard hover padding="lg">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3b82f6' }}>
          <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="8.5" cy="7" r="4" />
            <path d="M20 8v6M23 11h-6" />
          </svg>
        </div>
        <div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Total Users</p>
          <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>1,234</h3>
        </div>
      </div>
    </GlassCard>

    <GlassCard hover padding="lg">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981' }}>
          <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
        </div>
        <div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Completed</p>
          <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>856</h3>
        </div>
      </div>
    </GlassCard>

    <GlassCard hover padding="lg">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ef4444' }}>
          <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Issues</p>
          <h3 style={{ fontSize: '24px', fontWeight: 'bold' }}>23</h3>
        </div>
      </div>
    </GlassCard>
  </div>
);

// Feature Cards
export const FeatureCards = () => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
    <Card padding="lg">
      <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
        <svg width="28" height="28" fill="none" stroke="white" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
        </svg>
      </div>
      <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>Fast Performance</h3>
      <p style={{ fontSize: '14px', color: '#6b7280', lineHeight: '1.6' }}>
        Lightning-fast load times and smooth interactions for the best user experience.
      </p>
    </Card>

    <Card padding="lg">
      <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
        <svg width="28" height="28" fill="none" stroke="white" strokeWidth="2" viewBox="0 0 24 24">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      </div>
      <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>Secure by Default</h3>
      <p style={{ fontSize: '14px', color: '#6b7280', lineHeight: '1.6' }}>
        Enterprise-grade security with encryption and role-based access control.
      </p>
    </Card>

    <Card padding="lg">
      <div style={{ width: '56px', height: '56px', borderRadius: '12px', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
        <svg width="28" height="28" fill="none" stroke="white" strokeWidth="2" viewBox="0 0 24 24">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
      </div>
      <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>Real-time Updates</h3>
      <p style={{ fontSize: '14px', color: '#6b7280', lineHeight: '1.6' }}>
        Stay in sync with live data updates and collaborative features.
      </p>
    </Card>
  </div>
);
