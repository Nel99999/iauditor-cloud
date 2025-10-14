import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import MyApprovalsPage from '@/components/MyApprovalsPage';

const MyApprovalsPageNew = (props) => {
  return (
    <ModernPageWrapper title="My Approvals" subtitle="Review pending approvals">
      <MyApprovalsPage {...props} />
    </ModernPageWrapper>
  );
};

export default MyApprovalsPageNew;