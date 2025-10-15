import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ChecklistExecutionPage from '@/components/ChecklistExecutionPage';

const ChecklistExecutionPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Checklist Execution" subtitle="Complete checklist items">
      <ChecklistExecutionPage {...props} />
    </ModernPageWrapper>
  );
};

export default ChecklistExecutionPageNew;
