import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ChecklistExecutionPage from '@/components/ChecklistExecutionPage';

const ChecklistExecutionPageNew = (props) => {
  return (
    <ModernPageWrapper title="Execute Checklist">
      <ChecklistExecutionPage {...props} />
    </ModernPageWrapper>
  );
};

export default ChecklistExecutionPageNew;