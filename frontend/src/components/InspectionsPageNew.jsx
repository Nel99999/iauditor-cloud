import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import InspectionsPage from '@/components/InspectionsPage';

const InspectionsPageNew = (props) => {
  return (
    <ModernPageWrapper title="Inspections" subtitle="Manage inspections and audits">
      <InspectionsPage {...props} />
    </ModernPageWrapper>
  );
};

export default InspectionsPageNew;