import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import InspectionExecutionPage from '@/components/InspectionExecutionPage';

const InspectionExecutionPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Inspection Execution" subtitle="Conduct inspections">
      <InspectionExecutionPage {...props} />
    </ModernPageWrapper>
  );
};

export default InspectionExecutionPageNew;
