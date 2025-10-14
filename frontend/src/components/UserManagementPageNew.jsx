import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import UserManagementPage from '@/components/UserManagementPage';

const UserManagementPageNew = (props) => {
  return (
    <ModernPageWrapper title="User Management" subtitle="Manage system users and permissions">
      <UserManagementPage {...props} />
    </ModernPageWrapper>
  );
};

export default UserManagementPageNew;