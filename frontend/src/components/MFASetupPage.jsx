import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const MFASetupPage = () => {
  const { token } = useAuth();
  const [mfaStatus, setMfaStatus] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    fetchMFAStatus();
  }, []);

  const fetchMFAStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/mfa/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setMfaStatus(data);
    } catch (error) {
      console.error('Error fetching MFA status:', error);
    }
  };

  const handleSetupMFA = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      const response = await fetch(`${backendUrl}/api/mfa/setup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSetupData(data);
        setShowBackupCodes(true);
        setMessage({ type: 'success', text: 'MFA setup initiated. Scan the QR code with your authenticator app.' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to setup MFA' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyMFA = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setMessage({ type: 'error', text: 'Please enter a 6-digit code' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${backendUrl}/api/mfa/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: verificationCode })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'MFA enabled successfully!' });
        setSetupData(null);
        setShowBackupCodes(false);
        fetchMFAStatus();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Invalid verification code' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
      setVerificationCode('');
    }
  };

  const handleDisableMFA = async () => {
    const password = prompt('Enter your password to disable MFA:');
    if (!password) return;

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${backendUrl}/api/mfa/disable`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'MFA disabled successfully' });
        fetchMFAStatus();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to disable MFA' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateBackupCodes = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${backendUrl}/api/mfa/regenerate-backup-codes`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSetupData(data);
        setShowBackupCodes(true);
        setMessage({ type: 'success', text: 'Backup codes regenerated successfully' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to regenerate backup codes' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
        Multi-Factor Authentication
      </h1>

      {message.text && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {mfaStatus && (
        <div className="mb-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">MFA Status</h2>
          <div className="space-y-2">
            <p className="text-gray-700 dark:text-gray-300">
              <span className="font-medium">Status:</span>{' '}
              <span className={`font-bold ${mfaStatus.enabled ? 'text-green-600' : 'text-gray-500'}`}>
                {mfaStatus.enabled ? 'Enabled ✓' : 'Disabled'}
              </span>
            </p>
            {mfaStatus.enabled && (
              <p className="text-gray-700 dark:text-gray-300">
                <span className="font-medium">Backup Codes Remaining:</span> {mfaStatus.backup_codes_remaining}
              </p>
            )}
          </div>

          <div className="mt-6 flex gap-4">
            {!mfaStatus.enabled ? (
              <button
                onClick={handleSetupMFA}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              >
                {loading ? 'Setting up...' : 'Setup MFA'}
              </button>
            ) : (
              <>
                <button
                  onClick={handleRegenerateBackupCodes}
                  disabled={loading}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                >
                  Regenerate Backup Codes
                </button>
                <button
                  onClick={handleDisableMFA}
                  disabled={loading}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400"
                >
                  Disable MFA
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {setupData && (
        <div className="space-y-6">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Step 1: Scan QR Code</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </p>
            <div className="flex justify-center">
              <img src={setupData.qr_code} alt="MFA QR Code" className="border rounded-lg" />
            </div>
          </div>

          {showBackupCodes && setupData.backup_codes && (
            <div className="p-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg shadow border-2 border-yellow-400">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                ⚠️ Backup Codes
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
              </p>
              <div className="grid grid-cols-2 gap-2 mb-4 font-mono text-sm">
                {setupData.backup_codes.map((code, index) => (
                  <div key={index} className="p-2 bg-white dark:bg-gray-800 rounded border">
                    {code}
                  </div>
                ))}
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(setupData.backup_codes.join('\n'));
                  setMessage({ type: 'success', text: 'Backup codes copied to clipboard!' });
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Copy All Codes
              </button>
            </div>
          )}

          {!mfaStatus?.enabled && (
            <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Step 2: Verify Code
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Enter the 6-digit code from your authenticator app to complete setup:
              </p>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  maxLength={6}
                  className="flex-1 px-4 py-2 border rounded-lg text-center text-2xl tracking-widest dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                <button
                  onClick={handleVerifyMFA}
                  disabled={loading || verificationCode.length !== 6}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                >
                  Verify & Enable
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
          What is Multi-Factor Authentication?
        </h3>
        <p className="text-gray-700 dark:text-gray-300">
          MFA adds an extra layer of security to your account by requiring a second form of verification
          in addition to your password. Even if someone knows your password, they won't be able to access
          your account without the verification code from your authenticator app.
        </p>
      </div>
    </div>
  );
};

export default MFASetupPage;
