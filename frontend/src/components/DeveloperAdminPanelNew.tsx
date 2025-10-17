import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import DeveloperAdminPanelFull from '@/components/DeveloperAdminPanelFull';

const DeveloperAdminPanelNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Developer Admin" subtitle="Full DevOps Dashboard">
      <DeveloperAdminPanelFull {...props} />
    </ModernPageWrapper>
  );
};

export default DeveloperAdminPanelNew;
