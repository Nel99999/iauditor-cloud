import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import BulkImportPage from '@/components/BulkImportPage';

const BulkImportPageNew: React.FC = (props) => {
  return (
    <ModernPageWrapper title="Bulk Import" subtitle="Import users and data in bulk">
      <BulkImportPage {...props} />
    </ModernPageWrapper>
  );
};

export default BulkImportPageNew;
