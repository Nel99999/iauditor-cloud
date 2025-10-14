/**
 * HOC (Higher Order Component) to wrap existing pages with modern design
 * This allows us to quickly modernize pages without complete rewrites
 */
import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import './withModernDesign.css';

const withModernDesign = (WrappedComponent, config = {}) => {
  return (props) => {
    const { title, subtitle } = config;
    
    return (
      <div className="modern-page-hoc">
        <ModernPageWrapper title={title} subtitle={subtitle}>
          <div className="modern-content-wrapper">
            <WrappedComponent {...props} />
          </div>
        </ModernPageWrapper>
      </div>
    );
  };
};

export default withModernDesign;
