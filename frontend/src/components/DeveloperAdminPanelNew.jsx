import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import DeveloperAdminPanel from '@/components/DeveloperAdminPanel';

const DeveloperAdminPanelNew = (props) => {
  return (
    <ModernPageWrapper title="Developer Admin" subtitle="Advanced developer settings">
      <DeveloperAdminPanel {...props} />
    </ModernPageWrapper>
  );
};

export default DeveloperAdminPanelNew;