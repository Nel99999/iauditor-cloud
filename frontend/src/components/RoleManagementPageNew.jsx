import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import RoleManagementPage from '@/components/RoleManagementPage';

const RoleManagementPageNew = (props) => {
  return (
    <ModernPageWrapper title="Role Management" subtitle="Configure roles and access control">
      <RoleManagementPage {...props} />
    </ModernPageWrapper>
  );
};

export default RoleManagementPageNew;