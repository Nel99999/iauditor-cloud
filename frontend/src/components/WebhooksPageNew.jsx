import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import WebhooksPage from '@/components/WebhooksPage';

const WebhooksPageNew = (props) => {
  return (
    <ModernPageWrapper title="Webhooks" subtitle="Configure webhook integrations">
      <WebhooksPage {...props} />
    </ModernPageWrapper>
  );
};

export default WebhooksPageNew;