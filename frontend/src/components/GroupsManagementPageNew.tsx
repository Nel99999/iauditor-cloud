import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import GroupsManagementPage from '@/components/GroupsManagementPage';

const GroupsManagementPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Groups & Teams" subtitle="Organize users into groups">
      <GroupsManagementPage {...props} />
    </ModernPageWrapper>
  );
};

export default GroupsManagementPageNew;
