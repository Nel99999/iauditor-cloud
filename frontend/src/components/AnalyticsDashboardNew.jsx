import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';

const AnalyticsDashboardNew = (props) => {
  return (
    <ModernPageWrapper title="Analytics" subtitle="View system analytics and insights">
      <AnalyticsDashboard {...props} />
    </ModernPageWrapper>
  );
};

export default AnalyticsDashboardNew;