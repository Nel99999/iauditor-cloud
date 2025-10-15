import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import InvitationManagementPage from '@/components/InvitationManagementPage';

const InvitationManagementPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Invitations" subtitle="Manage user invitations">
      <InvitationManagementPage {...props} />
    </ModernPageWrapper>
  );
};

export default InvitationManagementPageNew;
