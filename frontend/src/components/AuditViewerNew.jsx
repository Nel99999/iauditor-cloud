import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import AuditViewer from '@/components/AuditViewer';

const AuditViewerNew = (props) => {
  return (
    <ModernPageWrapper title="Audit Trail" subtitle="View system audit logs">
      <AuditViewer {...props} />
    </ModernPageWrapper>
  );
};

export default AuditViewerNew;