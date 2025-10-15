import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import DelegationManager from '@/components/DelegationManager';

const DelegationManagerNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Delegations" subtitle="Manage authority delegations">
      <DelegationManager {...props} />
    </ModernPageWrapper>
  );
};

export default DelegationManagerNew;
