import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import MFASetupPage from '@/components/MFASetupPage';

const MFASetupPageNew: React.FC = () => {
  return (
    <ModernPageWrapper title="MFA Setup" subtitle="Configure multi-factor authentication">
      <MFASetupPage />
    </ModernPageWrapper>
  );
};

export default MFASetupPageNew;
