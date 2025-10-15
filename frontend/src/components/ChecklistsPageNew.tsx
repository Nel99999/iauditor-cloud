import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ChecklistsPage from '@/components/ChecklistsPage';

const ChecklistsPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Checklists" subtitle="Manage checklists and templates">
      <ChecklistsPage {...props} />
    </ModernPageWrapper>
  );
};

export default ChecklistsPageNew;
