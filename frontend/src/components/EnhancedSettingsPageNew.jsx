import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import EnhancedSettingsPage from '@/components/EnhancedSettingsPage';

const EnhancedSettingsPageNew = (props) => {
  return (
    <ModernPageWrapper title="Settings" subtitle="Configure system settings">
      <EnhancedSettingsPage {...props} />
    </ModernPageWrapper>
  );
};

export default EnhancedSettingsPageNew;