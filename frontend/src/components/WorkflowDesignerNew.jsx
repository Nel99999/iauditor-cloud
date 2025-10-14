import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import WorkflowDesigner from '@/components/WorkflowDesigner';

const WorkflowDesignerNew = (props) => {
  return (
    <ModernPageWrapper title="Workflow Designer" subtitle="Design and manage workflows">
      <WorkflowDesigner {...props} />
    </ModernPageWrapper>
  );
};

export default WorkflowDesignerNew;