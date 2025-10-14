import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import GroupsManagementPage from '@/components/GroupsManagementPage';

const GroupsManagementPageNew = (props) => {
  return (
    <ModernPageWrapper title="Groups" subtitle="Manage user groups">
      <GroupsManagementPage {...props} />
    </ModernPageWrapper>
  );
};

export default GroupsManagementPageNew;