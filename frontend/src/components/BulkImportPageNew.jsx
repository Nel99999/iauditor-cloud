import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import BulkImportPage from '@/components/BulkImportPage';

const BulkImportPageNew = (props) => {
  return (
    <ModernPageWrapper title="Bulk Import" subtitle="Import data in bulk">
      <BulkImportPage {...props} />
    </ModernPageWrapper>
  );
};

export default BulkImportPageNew;