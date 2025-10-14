import React from 'react';
import './ModernPageWrapper.css';

interface ModernPageWrapperProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

/**
 * ModernPageWrapper - Wraps any page content with modern design elements
 * Adds gradient background and proper spacing without modifying page internals
 */
const ModernPageWrapper: React.FC<ModernPageWrapperProps> = ({ children, title, subtitle, actions }) => {
  return (
    <div className="modern-page-wrapper">
      {/* Animated Background */}
      <div className="page-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      {/* Page Header */}
      {(title || actions) && (
        <div className="page-header-modern">
          <div className="page-header-content">
            {title && (
              <div className="page-title-section">
                <h1 className="page-title-modern">{title}</h1>
                {subtitle && <p className="page-subtitle-modern">{subtitle}</p>}
              </div>
            )}
            {actions && <div className="page-actions-modern">{actions}</div>}
          </div>
        </div>
      )}

      {/* Page Content */}
      <div className="page-content-modern">
        {children}
      </div>
    </div>
  );
};

export default ModernPageWrapper;
