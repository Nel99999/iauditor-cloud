import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ResetPasswordPage from '@/components/ResetPasswordPage';

const ResetPasswordPageNew = (props) => {
  return (
    <div className="reset-password-wrapper">
      <ResetPasswordPage {...props} />
    </div>
  );
};

export default ResetPasswordPageNew;