import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ReportsPage from '@/components/ReportsPage';

const ReportsPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Reports" subtitle="View and generate reports">
      <ReportsPage {...props} />
    </ModernPageWrapper>
  );
};

export default ReportsPageNew;
