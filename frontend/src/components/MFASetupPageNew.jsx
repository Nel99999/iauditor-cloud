import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import MFASetupPage from '@/components/MFASetupPage';

const MFASetupPageNew = (props) => {
  return (
    <ModernPageWrapper title="MFA Setup" subtitle="Configure multi-factor authentication">
      <MFASetupPage {...props} />
    </ModernPageWrapper>
  );
};

export default MFASetupPageNew;