import React, { useState } from 'react';
import { Button, Card, GlassCard, Input } from '@/design-system/components';
import { useTheme } from '@/contexts/ThemeContext';
import { Sun, Moon, Check, X, AlertCircle } from 'lucide-react';

const DesignSystemShowcase: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [inputValue, setInputValue] = useState('');

  return (
    <div style={{
      minHeight: '100vh',
      padding: 'var(--spacing-8)',
      backgroundColor: 'var(--color-surface-base)',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--spacing-8)'
      }}>
        <div>
          <h1 style={{
            fontSize: 'var(--typography-size-4xl)',
            fontWeight: 'var(--typography-weight-bold)',
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-2)'
          }}>
            Design System Showcase
          </h1>
          <p style={{
            fontSize: 'var(--typography-size-lg)',
            color: 'var(--color-text-secondary)'
          }}>
            Dark Mode First • Token-Driven • Modern
          </p>
        </div>
        <Button
          variant="ghost"
          size="lg"
          icon={theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          onClick={toggleTheme}
        >
          Toggle Theme
        </Button>
      </div>

      {/* Buttons Section */}
      <GlassCard padding="lg" style={{ marginBottom: 'var(--spacing-6)' }}>
        <h2 style={{
          fontSize: 'var(--typography-size-2xl)',
          fontWeight: 'var(--typography-weight-semibold)',
          color: 'var(--color-text-primary)',
          marginBottom: 'var(--spacing-4)'
        }}>
          Buttons
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-4)' }}>
          <Button variant="primary" size="sm">Small Primary</Button>
          <Button variant="primary" size="md">Medium Primary</Button>
          <Button variant="primary" size="lg">Large Primary</Button>
          <Button variant="accent" size="md" icon={<Check size={18} />}>With Icon</Button>
          <Button variant="secondary" size="md">Secondary</Button>
          <Button variant="ghost" size="md">Ghost</Button>
          <Button variant="destructive" size="md" icon={<X size={18} />}>Destructive</Button>
          <Button variant="primary" size="md" disabled>Disabled</Button>
          <Button variant="primary" size="md" loading>Loading</Button>
        </div>
      </GlassCard>

      {/* Cards Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 'var(--spacing-6)',
        marginBottom: 'var(--spacing-6)'
      }}>
        <Card hover padding="lg">
          <h3 style={{
            fontSize: 'var(--typography-size-xl)',
            fontWeight: 'var(--typography-weight-semibold)',
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-3)'
          }}>
            Regular Card
          </h3>
          <p style={{
            fontSize: 'var(--typography-size-base)',
            color: 'var(--color-text-secondary)',
            lineHeight: '1.6'
          }}>
            This is a regular card component with hover effect. It uses token-driven styling for consistency.
          </p>
        </Card>

        <GlassCard hover padding="lg">
          <h3 style={{
            fontSize: 'var(--typography-size-xl)',
            fontWeight: 'var(--typography-weight-semibold)',
            color: 'var(--color-text-primary)',
            marginBottom: 'var(--spacing-3)'
          }}>
            Glass Card ✨
          </h3>
          <p style={{
            fontSize: 'var(--typography-size-base)',
            color: 'var(--color-text-secondary)',
            lineHeight: '1.6'
          }}>
            This is a glassmorphism card with backdrop blur. Perfect for modern, layered UIs.
          </p>
        </GlassCard>

        <Card hover padding="lg" style={{
          background: `linear-gradient(135deg, var(--color-brand-primary), var(--color-brand-accent))`,
        }}>
          <h3 style={{
            fontSize: 'var(--typography-size-xl)',
            fontWeight: 'var(--typography-weight-semibold)',
            color: 'var(--color-brand-primary-contrast)',
            marginBottom: 'var(--spacing-3)'
          }}>
            Gradient Card
          </h3>
          <p style={{
            fontSize: 'var(--typography-size-base)',
            color: 'var(--color-brand-primary-contrast)',
            lineHeight: '1.6',
            opacity: 0.9
          }}>
            Cards can have custom styles while still using token values.
          </p>
        </Card>
      </div>

      {/* Inputs Section */}
      <GlassCard padding="lg" style={{ marginBottom: 'var(--spacing-6)' }}>
        <h2 style={{
          fontSize: 'var(--typography-size-2xl)',
          fontWeight: 'var(--typography-weight-semibold)',
          color: 'var(--color-text-primary)',
          marginBottom: 'var(--spacing-4)'
        }}>
          Inputs
        </h2>
        <div style={{ display: 'grid', gap: 'var(--spacing-4)', maxWidth: '600px' }}>
          <div>
            <label style={{
              display: 'block',
              fontSize: 'var(--typography-size-sm)',
              fontWeight: 'var(--typography-weight-medium)',
              color: 'var(--color-text-primary)',
              marginBottom: 'var(--spacing-2)'
            }}>
              Small Input
            </label>
            <Input
              size="sm"
              placeholder="Enter text..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
          </div>
          <div>
            <label style={{
              display: 'block',
              fontSize: 'var(--typography-size-sm)',
              fontWeight: 'var(--typography-weight-medium)',
              color: 'var(--color-text-primary)',
              marginBottom: 'var(--spacing-2)'
            }}>
              Medium Input with Icon
            </label>
            <Input
              size="md"
              placeholder="With icon..."
              icon={<AlertCircle size={18} />}
            />
          </div>
          <div>
            <label style={{
              display: 'block',
              fontSize: 'var(--typography-size-sm)',
              fontWeight: 'var(--typography-weight-medium)',
              color: 'var(--color-text-primary)',
              marginBottom: 'var(--spacing-2)'
            }}>
              Large Input
            </label>
            <Input
              size="lg"
              placeholder="Large size..."
            />
          </div>
          <div>
            <label style={{
              display: 'block',
              fontSize: 'var(--typography-size-sm)',
              fontWeight: 'var(--typography-weight-medium)',
              color: 'var(--color-semantic-error)',
              marginBottom: 'var(--spacing-2)'
            }}>
              Error State
            </label>
            <Input
              size="md"
              error
              placeholder="Error state..."
            />
          </div>
          <div>
            <label style={{
              display: 'block',
              fontSize: 'var(--typography-size-sm)',
              fontWeight: 'var(--typography-weight-medium)',
              color: 'var(--color-text-disabled)',
              marginBottom: 'var(--spacing-2)'
            }}>
              Disabled
            </label>
            <Input
              size="md"
              disabled
              placeholder="Disabled..."
            />
          </div>
        </div>
      </GlassCard>

      {/* Color Palette */}
      <GlassCard padding="lg">
        <h2 style={{
          fontSize: 'var(--typography-size-2xl)',
          fontWeight: 'var(--typography-weight-semibold)',
          color: 'var(--color-text-primary)',
          marginBottom: 'var(--spacing-4)'
        }}>
          Color Palette
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 'var(--spacing-4)' }}>
          {[
            { name: 'Primary', color: 'var(--color-brand-primary)' },
            { name: 'Accent', color: 'var(--color-brand-accent)' },
            { name: 'Success', color: 'var(--color-semantic-success)' },
            { name: 'Warning', color: 'var(--color-semantic-warning)' },
            { name: 'Error', color: 'var(--color-semantic-error)' },
            { name: 'Info', color: 'var(--color-semantic-info)' },
          ].map(({ name, color }) => (
            <div key={name} style={{
              padding: 'var(--spacing-4)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: color,
              color: 'var(--color-brand-primary-contrast)',
              textAlign: 'center',
              fontWeight: 'var(--typography-weight-semibold)',
              fontSize: 'var(--typography-size-sm)',
              boxShadow: 'var(--shadow-md)'
            }}>
              {name}
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

export default DesignSystemShowcase;