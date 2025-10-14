import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ChecklistsPage from '@/components/ChecklistsPage';

const ChecklistsPageNew = (props) => {
  return (
    <ModernPageWrapper title="Checklists" subtitle="Create and manage checklists">
      <ChecklistsPage {...props} />
    </ModernPageWrapper>
  );
};

export default ChecklistsPageNew;