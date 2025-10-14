import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import InspectionExecutionPage from '@/components/InspectionExecutionPage';

const InspectionExecutionPageNew = (props) => {
  return (
    <ModernPageWrapper title="Execute Inspection">
      <InspectionExecutionPage {...props} />
    </ModernPageWrapper>
  );
};

export default InspectionExecutionPageNew;