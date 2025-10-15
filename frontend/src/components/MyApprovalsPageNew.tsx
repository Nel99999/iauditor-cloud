import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import MyApprovalsPage from '@/components/MyApprovalsPage';

const MyApprovalsPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="My Approvals" subtitle="Review and approve pending items">
      <MyApprovalsPage {...props} />
    </ModernPageWrapper>
  );
};

export default MyApprovalsPageNew;
