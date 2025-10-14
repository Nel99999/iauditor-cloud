import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import OrganizationPage from '@/components/OrganizationPage';

const OrganizationPageNew = (props) => {
  return (
    <ModernPageWrapper title="Organization" subtitle="Manage organizational structure">
      <OrganizationPage {...props} />
    </ModernPageWrapper>
  );
};

export default OrganizationPageNew;