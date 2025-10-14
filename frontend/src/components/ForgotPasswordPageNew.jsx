import React from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import ForgotPasswordPage from '@/components/ForgotPasswordPage';

const ForgotPasswordPageNew = (props) => {
  return (
    <div className="forgot-password-wrapper">
      <ForgotPasswordPage {...props} />
    </div>
  );
};

export default ForgotPasswordPageNew;