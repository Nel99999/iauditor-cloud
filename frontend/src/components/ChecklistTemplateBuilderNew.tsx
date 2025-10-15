import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ChecklistTemplateBuilder from '@/components/ChecklistTemplateBuilder';

const ChecklistTemplateBuilderNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Checklist Template Builder" subtitle="Build checklist templates">
      <ChecklistTemplateBuilder {...props} />
    </ModernPageWrapper>
  );
};

export default ChecklistTemplateBuilderNew;
