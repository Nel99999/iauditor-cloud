import React, { useState } from 'react';
import {
  Button,
  GlassCard,
  Skeleton,
  ToastContainer,
  EmptyState,
  Spinner
} from '@/design-system/components';
import { FileX, Plus } from 'lucide-react';
import './VisualPolishShowcase.css';

// Types
interface ToastItem {
  id: string;
  type: string;
  message: string;
  duration: number;
}

const VisualPolishShowcase = () => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const addToast = (type: string, message: string): void => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, type, message, duration: 3000 }]);
  };

  const removeToast = (id: string): void => {
    setToasts(prev => prev.filter((toast: any) => toast.id !== id));
  };

  const simulateLoading = (): void => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 3000);
  };

  return (
    <div className="visual-polish-showcase">
      {/* Toast Container */}
      <ToastContainer toasts={toasts as any} removeToast={removeToast} />

      <div className="showcase-header">
        <h1 className="showcase-title">Phase 6: Visual Polish</h1>
        <p className="showcase-subtitle">
          Micro-interactions, Loading States & Delightful UI
        </p>
      </div>

      {/* Spinners Section */}
      <GlassCard padding="lg" className="showcase-section">
        <h2 className="section-title">Spinners</h2>
        <div className="spinners-grid">
          <div className="spinner-demo">
            <Spinner size="sm" color="primary" />
            <span>Small</span>
          </div>
          <div className="spinner-demo">
            <Spinner size="md" color="primary" />
            <span>Medium</span>
          </div>
          <div className="spinner-demo">
            <Spinner size="lg" color="accent" />
            <span>Large</span>
          </div>
          <div className="spinner-demo">
            <Spinner size="xl" color="primary" />
            <span>Extra Large</span>
          </div>
        </div>
      </GlassCard>

      {/* Skeleton Loaders */}
      <GlassCard padding="lg" className="showcase-section">
        <h2 className="section-title">Skeleton Loaders</h2>
        <div className="skeleton-demo">
          <div className="skeleton-item">
            <Skeleton variant="circular" width="48px" height="48px" />
            <div style={{ flex: 1 }}>
              <Skeleton width="60%" height="16px" />
              <Skeleton width="40%" height="12px" className="mt-2" />
            </div>
          </div>
          <div className="skeleton-item">
            <Skeleton variant="rectangular" width="100%" height="200px" />
          </div>
          <div className="skeleton-item">
            <Skeleton width="100%" height="16px" />
            <Skeleton width="90%" height="16px" />
            <Skeleton width="70%" height="16px" />
          </div>
        </div>
      </GlassCard>

      {/* Toast Notifications */}
      <GlassCard padding="lg" className="showcase-section">
        <h2 className="section-title">Toast Notifications</h2>
        <div className="toast-buttons">
          <Button
            variant="primary"
            onClick={() => addToast('success', 'Changes saved successfully!')}
          >
            Success Toast
          </Button>
          <Button
            variant="danger"
            onClick={() => addToast('error', 'Something went wrong!')}
          >
            Error Toast
          </Button>
          <Button
            variant="secondary"
            onClick={() => addToast('warning', 'Please review your changes')}
          >
            Warning Toast
          </Button>
          <Button
            variant="secondary"
            onClick={() => addToast('info', 'New update available')}
          >
            Info Toast
          </Button>
        </div>
      </GlassCard>

      {/* Empty States */}
      <GlassCard padding="lg" className="showcase-section">
        <h2 className="section-title">Empty States</h2>
        <EmptyState
          title="No tasks found"
          description="Get started by creating your first task. Tasks help you organize and track your work efficiently."
          icon={FileX}
          action={
            <Button variant="primary" icon={<Plus size={18} />}>
              Create Task
            </Button>
          }
        />
      </GlassCard>

      {/* Loading State Demo */}
      <GlassCard padding="lg" className="showcase-section">
        <h2 className="section-title">Loading State Demo</h2>
        <div className="loading-demo">
          <Button
            variant="primary"
            onClick={simulateLoading}
            disabled={isLoading}
          >
            Simulate Loading
          </Button>

          {isLoading && (
            <div className="loading-content">
              <Spinner size="lg" />
              <p>Loading your content...</p>
            </div>
          )}

          {!isLoading && (
            <div className="loaded-content">
              <p className="loaded-text">✨ Content loaded successfully!</p>
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
};

export default VisualPolishShowcase;
