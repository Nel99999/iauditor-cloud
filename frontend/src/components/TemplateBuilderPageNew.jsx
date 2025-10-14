import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import TemplateBuilderPage from '@/components/TemplateBuilderPage';

const TemplateBuilderPageNew = (props) => {
  return (
    <ModernPageWrapper title="Template Builder" subtitle="Build inspection templates">
      <TemplateBuilderPage {...props} />
    </ModernPageWrapper>
  );
};

export default TemplateBuilderPageNew;