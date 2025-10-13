import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useTranslation } from 'react-i18next';
import { usePermissions } from '../hooks/usePermissions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Settings, User, Shield, Bell, Building2, Save, Upload, Eye, EyeOff, Key, CheckCircle, XCircle, Moon, Sun, Globe, Lock, Clock, AlertTriangle } from 'lucide-react';
import 'react-phone-number-input/style.css';
import PhoneInput from 'react-phone-number-input';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EnhancedSettingsPage = () => {
  const { user, setUser } = useAuth();
  const { theme, toggleTheme, accentColor, updateAccentColor, viewDensity, updateViewDensity, fontSize, updateFontSize } = useTheme();
  const { t, i18n } = useTranslation();
  const { isAdmin, isDeveloper, isDeveloperOrMaster } = usePermissions();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Profile
  const [profileData, setProfileData] = useState({ name: '', phone: '', bio: '' });
  
  // Security
  const [passwordData, setPasswordData] = useState({ current_password: '', new_password: '', confirm_password: '' });
  
  // Regional
  const [regionalPrefs, setRegionalPrefs] = useState({
    language: 'en',
    timezone: 'UTC',
    date_format: 'MM/DD/YYYY',
    time_format: '12h',
    currency: 'USD'
  });
  
  // Privacy
  const [privacyPrefs, setPrivacyPrefs] = useState({
    profile_visibility: 'organization',
    show_activity_status: true,
    show_last_seen: true
  });
  
  // Security Prefs
  const [securityPrefs, setSecurityPrefs] = useState({
    two_factor_enabled: false,
    session_timeout: 3600
  });
  
  // Notifications
  const [notificationPrefs, setNotificationPrefs] = useState({
    emailNotifications: true,
    pushNotifications: false,
    weeklyReports: true,
    marketingEmails: false
  });
  
  // GDPR
  const [gdprConsents, setGdprConsents] = useState({
    marketing: false,
    analytics: false,
    third_party: false
  });
  const [exportingData, setExportingData] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);
  
  // API Settings
  const [apiSettings, setApiSettings] = useState({
    sendgrid_api_key: '',
    sendgrid_configured: false
  });
  const [testingEmail, setTestingEmail] = useState(false);
  const [emailTestResult, setEmailTestResult] = useState(null);
  
  // Twilio Settings
  const [twilioSettings, setTwilioSettings] = useState({
    account_sid: '',
    auth_token: '',
    phone_number: '',
    whatsapp_number: '',
    twilio_configured: false
  });
  const [testingTwilio, setTestingTwilio] = useState(false);
  const [twilioTestResult, setTwilioTestResult] = useState(null);
  
  // Test SMS/WhatsApp
  const [testSMSPhone, setTestSMSPhone] = useState('');
  const [testWhatsAppPhone, setTestWhatsAppPhone] = useState('');
  const [sendingSMS, setSendingSMS] = useState(false);
  const [sendingWhatsApp, setSendingWhatsApp] = useState(false);
  const [smsTestResult, setSmsTestResult] = useState(null);
  const [whatsappTestResult, setWhatsappTestResult] = useState(null);

  useEffect(() => {
    if (user) {
      setProfileData({ name: user.name || '', phone: user.phone || '', bio: user.bio || '' });
      loadAllPreferences();
    }
  }, [user]);

  const loadAllPreferences = async () => {
    try {
      const [regional, privacy, security, api, twilio] = await Promise.all([
        axios.get(`${API}/users/regional`),
        axios.get(`${API}/users/privacy`),
        axios.get(`${API}/users/security-prefs`),
        isAdmin() || isDeveloper() ? axios.get(`${API}/settings/email`) : Promise.resolve({ data: {} }),
        isAdmin() || isDeveloper() ? axios.get(`${API}/sms/settings`) : Promise.resolve({ data: {} })
      ]);
      
      setRegionalPrefs(regional.data);
      setPrivacyPrefs(privacy.data);
      setSecurityPrefs(security.data);
      if (api.data) setApiSettings(api.data);
      if (twilio.data) setTwilioSettings({
        account_sid: twilio.data.account_sid || '',
        auth_token: '',
        phone_number: twilio.data.phone_number || '',
        whatsapp_number: twilio.data.whatsapp_number || '',
        twilio_configured: twilio.data.twilio_configured || false
      });
    } catch (err) {
      console.error('Failed to load preferences:', err);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.put(`${API}/users/${user.id}`, profileData);
      setUser({ ...user, ...profileData });
      showMessage('success', 'Profile updated successfully!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      showMessage('error', 'Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await axios.put(`${API}/users/${user.id}/password`, {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      showMessage('success', 'Password updated successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update password');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/users/profile/picture`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUser({ ...user, picture: response.data.picture_url });
      showMessage('success', 'Photo uploaded successfully!');
      window.location.reload();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to upload photo');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRegional = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/regional`, regionalPrefs);
      i18n.changeLanguage(regionalPrefs.language);
      showMessage('success', 'Regional settings saved!');
    } catch (err) {
      showMessage('error', 'Failed to save regional settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrivacy = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/privacy`, privacyPrefs);
      showMessage('success', 'Privacy settings saved!');
    } catch (err) {
      showMessage('error', 'Failed to save privacy settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSecurity = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/security-prefs`, securityPrefs);
      showMessage('success', 'Security settings saved!');
    } catch (err) {
      showMessage('error', 'Failed to save security settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotifications = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/settings`, notificationPrefs);
      showMessage('success', 'Notification preferences saved!');
    } catch (err) {
      showMessage('error', 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/settings/email`, { sendgrid_api_key: apiSettings.sendgrid_api_key });
      showMessage('success', 'SendGrid API key saved!');
      loadAllPreferences();
    } catch (err) {
      showMessage('error', 'Failed to save API key');
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    setTestingEmail(true);
    setEmailTestResult(null);
    try {
      const response = await axios.post(`${API}/settings/email/test`);
      setEmailTestResult({ success: true, message: response.data.message });
    } catch (err) {
      setEmailTestResult({ success: false, message: err.response?.data?.detail || 'Test failed' });
    } finally {
      setTestingEmail(false);
    }
  };

  const handleSaveTwilioSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/sms/settings`, {
        account_sid: twilioSettings.account_sid,
        auth_token: twilioSettings.auth_token,
        phone_number: twilioSettings.phone_number,
        whatsapp_number: twilioSettings.whatsapp_number
      });
      showMessage('success', 'Twilio settings saved successfully!');
      loadAllPreferences();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save Twilio settings');
    } finally {
      setLoading(false);
    }
  };

  const handleTestTwilio = async () => {
    setTestingTwilio(true);
    setTwilioTestResult(null);
    try {
      const response = await axios.post(`${API}/sms/test-connection`);
      setTwilioTestResult({ 
        success: true, 
        message: `Connected to ${response.data.data.friendly_name}`,
        account_sid: response.data.data.account_sid
      });
    } catch (err) {
      setTwilioTestResult({ 
        success: false, 
        message: err.response?.data?.detail || 'Connection failed' 
      });
    } finally {
      setTestingTwilio(false);
    }
  };

  const handleTestSMS = async () => {
    if (!testSMSPhone) {
      showMessage('error', 'Please enter a phone number');
      return;
    }
    setSendingSMS(true);
    setSmsTestResult(null);
    try {
      const response = await axios.post(`${API}/sms/send`, {
        to_number: testSMSPhone,
        message: 'This is a test SMS from your Operational Management Platform. Your Twilio SMS integration is working correctly!'
      });
      setSmsTestResult({ 
        success: true, 
        message: `SMS sent successfully! Message SID: ${response.data.message_sid}` 
      });
    } catch (err) {
      setSmsTestResult({ 
        success: false, 
        message: err.response?.data?.detail || 'Failed to send SMS' 
      });
    } finally {
      setSendingSMS(false);
    }
  };

  const handleTestWhatsApp = async () => {
    if (!testWhatsAppPhone) {
      showMessage('error', 'Please enter a phone number');
      return;
    }
    setSendingWhatsApp(true);
    setWhatsappTestResult(null);
    try {
      const response = await axios.post(`${API}/sms/whatsapp/send`, {
        to_number: testWhatsAppPhone,
        message: 'This is a test WhatsApp message from your Operational Management Platform. Your Twilio WhatsApp integration is working correctly!'
      });
      setWhatsappTestResult({ 
        success: true, 
        message: `WhatsApp message sent successfully! Message SID: ${response.data.message_sid}` 
      });
    } catch (err) {
      setWhatsappTestResult({ 
        success: false, 
        message: err.response?.data?.detail || 'Failed to send WhatsApp message' 
      });
    } finally {
      setSendingWhatsApp(false);
    }
  };

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'zh', name: '中文', flag: '🇨🇳' }
  ];

  const timezones = ['UTC', 'America/New_York', 'America/Los_Angeles', 'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney', 'Africa/Johannesburg'];
  const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'ZAR'];

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Settings className="h-8 w-8" />
          Settings
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">Manage your account settings and preferences</p>
      </div>

      {message.text && (
        <Alert className={`mb-6 ${message.type === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
          <AlertDescription className={message.type === 'success' ? 'text-green-800' : 'text-red-800'}>
            {message.text}
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${(isAdmin() || isDeveloper()) ? 8 : 7}, 1fr)` }}>
          <TabsTrigger value="profile">
            <User className="h-4 w-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Moon className="h-4 w-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="regional">
            <Globe className="h-4 w-4 mr-2" />
            Regional
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="privacy">
            <Lock className="h-4 w-4 mr-2" />
            Privacy
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="gdpr">
            <Shield className="h-4 w-4 mr-2" />
            GDPR & Privacy
          </TabsTrigger>
          {(isAdmin() || isDeveloper()) && (
            <TabsTrigger value="api">
              <Key className="h-4 w-4 mr-2" />
              API
            </TabsTrigger>
          )}
          {(isAdmin() || isDeveloper()) && (
            <TabsTrigger value="organization">
              <Building2 className="h-4 w-4 mr-2" />
              Organization
            </TabsTrigger>
          )}
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal information</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-6">
                <div className="flex items-center gap-6">
                  <div className="relative">
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-3xl font-bold overflow-hidden">
                      {user?.picture ? (
                        <img 
                          src={user.picture.startsWith('http') ? user.picture : `${BACKEND_URL}${user.picture}`} 
                          alt="Profile" 
                          className="w-full h-full object-cover" 
                        />
                      ) : (
                        user?.name?.charAt(0).toUpperCase()
                      )}
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="photo" className="cursor-pointer">
                      <div className="flex items-center gap-2 px-4 py-2 border rounded-md hover:bg-slate-50 dark:hover:bg-slate-800">
                        <Upload className="h-4 w-4" />
                        Upload Photo
                      </div>
                    </Label>
                    <Input id="photo" type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    <p className="text-xs text-slate-500 mt-1">JPG, PNG or GIF (max 5MB)</p>
                  </div>
                </div>

                <Separator />

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" value={profileData.name} onChange={(e) => setProfileData({...profileData, name: e.target.value})} required />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <PhoneInput value={profileData.phone} onChange={(value) => setProfileData({...profileData, phone: value})} defaultCountry="US" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                  </div>
                </div>

                <div>
                  <Label htmlFor="bio">Bio</Label>
                  <textarea id="bio" value={profileData.bio} onChange={(e) => setProfileData({...profileData, bio: e.target.value})} className="w-full h-24 px-3 py-2 border rounded-md" placeholder="Tell us about yourself..." />
                </div>

                <Button type="submit" disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>Customize how the application looks</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Theme</Label>
                  <p className="text-sm text-muted-foreground">Switch between light and dark mode</p>
                </div>
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
                  <Moon className="h-4 w-4" />
                </div>
              </div>

              <Separator />

              <div>
                <Label>Accent Color</Label>
                <p className="text-sm text-muted-foreground mb-2">Choose your preferred accent color</p>
                <div className="flex gap-2">
                  {['#6366f1', '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'].map(color => (
                    <button key={color} onClick={() => updateAccentColor(color)} className={`w-10 h-10 rounded-full border-2 ${accentColor === color ? 'border-slate-900 dark:border-white' : 'border-transparent'}`} style={{ backgroundColor: color }} />
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <Label>View Density</Label>
                <p className="text-sm text-muted-foreground mb-2">Adjust spacing and layout density</p>
                <div className="flex gap-2">
                  {['compact', 'comfortable', 'spacious'].map(density => (
                    <Button key={density} variant={viewDensity === density ? 'default' : 'outline'} onClick={() => updateViewDensity(density)} className="flex-1">
                      {density.charAt(0).toUpperCase() + density.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <Label>Font Size</Label>
                <p className="text-sm text-muted-foreground mb-2">Adjust text size throughout the app</p>
                <div className="flex gap-2">
                  {['small', 'medium', 'large'].map(size => (
                    <Button key={size} variant={fontSize === size ? 'default' : 'outline'} onClick={() => updateFontSize(size)} className="flex-1">
                      {size.charAt(0).toUpperCase() + size.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Regional Tab */}
        <TabsContent value="regional">
          <Card>
            <CardHeader>
              <CardTitle>Regional Settings</CardTitle>
              <CardDescription>Set your location and format preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label>Language</Label>
                <Select value={regionalPrefs.language} onValueChange={(value) => setRegionalPrefs({...regionalPrefs, language: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map(lang => (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.flag} {lang.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Timezone</Label>
                <Select value={regionalPrefs.timezone} onValueChange={(value) => setRegionalPrefs({...regionalPrefs, timezone: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {timezones.map(tz => (
                      <SelectItem key={tz} value={tz}>{tz}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Date Format</Label>
                  <Select value={regionalPrefs.date_format} onValueChange={(value) => setRegionalPrefs({...regionalPrefs, date_format: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                      <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                      <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Time Format</Label>
                  <Select value={regionalPrefs.time_format} onValueChange={(value) => setRegionalPrefs({...regionalPrefs, time_format: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="12h">12-hour</SelectItem>
                      <SelectItem value="24h">24-hour</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label>Currency</Label>
                <Select value={regionalPrefs.currency} onValueChange={(value) => setRegionalPrefs({...regionalPrefs, currency: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map(curr => (
                      <SelectItem key={curr} value={curr}>{curr}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handleSaveRegional} disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? 'Saving...' : 'Save Regional Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Change Password</CardTitle>
                <CardDescription>Update your password regularly for security</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <Label htmlFor="current">Current Password</Label>
                    <Input id="current" type="password" value={passwordData.current_password} onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})} required />
                  </div>
                  <div>
                    <Label htmlFor="new">New Password</Label>
                    <Input id="new" type="password" value={passwordData.new_password} onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})} required />
                  </div>
                  <div>
                    <Label htmlFor="confirm">Confirm New Password</Label>
                    <Input id="confirm" type="password" value={passwordData.confirm_password} onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})} required />
                  </div>
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Password'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Security Preferences</CardTitle>
                <CardDescription>Advanced security settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base">Two-Factor Authentication (2FA)</Label>
                    <p className="text-sm text-muted-foreground">Add an extra layer of security</p>
                  </div>
                  <Switch checked={securityPrefs.two_factor_enabled} onCheckedChange={(checked) => setSecurityPrefs({...securityPrefs, two_factor_enabled: checked})} />
                </div>

                <Separator />

                <div>
                  <Label>Session Timeout</Label>
                  <p className="text-sm text-muted-foreground mb-2">Automatically log out after inactivity</p>
                  <Select value={securityPrefs.session_timeout.toString()} onValueChange={(value) => setSecurityPrefs({...securityPrefs, session_timeout: parseInt(value)})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="900">15 minutes</SelectItem>
                      <SelectItem value="1800">30 minutes</SelectItem>
                      <SelectItem value="3600">1 hour</SelectItem>
                      <SelectItem value="14400">4 hours</SelectItem>
                      <SelectItem value="0">Never</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button onClick={handleSaveSecurity} disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Security Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Privacy Tab */}
        <TabsContent value="privacy">
          <Card>
            <CardHeader>
              <CardTitle>Privacy Settings</CardTitle>
              <CardDescription>Control who can see your information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label>Profile Visibility</Label>
                <p className="text-sm text-muted-foreground mb-2">Who can see your profile</p>
                <Select value={privacyPrefs.profile_visibility} onValueChange={(value) => setPrivacyPrefs({...privacyPrefs, profile_visibility: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="public">Public - Everyone</SelectItem>
                    <SelectItem value="organization">Organization - Only team members</SelectItem>
                    <SelectItem value="private">Private - Only me</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Show Activity Status</Label>
                  <p className="text-sm text-muted-foreground">Let others see when you're online</p>
                </div>
                <Switch checked={privacyPrefs.show_activity_status} onCheckedChange={(checked) => setPrivacyPrefs({...privacyPrefs, show_activity_status: checked})} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Show Last Seen</Label>
                  <p className="text-sm text-muted-foreground">Display when you were last active</p>
                </div>
                <Switch checked={privacyPrefs.show_last_seen} onCheckedChange={(checked) => setPrivacyPrefs({...privacyPrefs, show_last_seen: checked})} />
              </div>

              <Button onClick={handleSavePrivacy} disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                Save Privacy Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Manage how you receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                </div>
                <Switch checked={notificationPrefs.emailNotifications} onCheckedChange={(checked) => setNotificationPrefs({...notificationPrefs, emailNotifications: checked})} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Push Notifications</Label>
                  <p className="text-sm text-muted-foreground">Get browser push notifications</p>
                </div>
                <Switch checked={notificationPrefs.pushNotifications} onCheckedChange={(checked) => setNotificationPrefs({...notificationPrefs, pushNotifications: checked})} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Weekly Reports</Label>
                  <p className="text-sm text-muted-foreground">Receive weekly summary emails</p>
                </div>
                <Switch checked={notificationPrefs.weeklyReports} onCheckedChange={(checked) => setNotificationPrefs({...notificationPrefs, weeklyReports: checked})} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base">Marketing Emails</Label>
                  <p className="text-sm text-muted-foreground">Receive product updates and tips</p>
                </div>
                <Switch checked={notificationPrefs.marketingEmails} onCheckedChange={(checked) => setNotificationPrefs({...notificationPrefs, marketingEmails: checked})} />
              </div>

              <Button onClick={handleSaveNotifications} disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                Save Notification Preferences
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Tab */}
        {(isAdmin() || isDeveloper()) && (
          <TabsContent value="api">
            <Card>
              <CardHeader>
                <CardTitle>API Configuration</CardTitle>
                <CardDescription>Manage third-party API keys for email and integrations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label>SendGrid API Key</Label>
                  <p className="text-xs text-muted-foreground mb-2">
                    Required for sending invitation emails. Get your API key from{' '}
                    <a href="https://app.sendgrid.com/settings/api_keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">SendGrid Dashboard</a>
                  </p>
                  <div className="flex gap-2">
                    <Input type="password" placeholder={apiSettings.sendgrid_configured ? "API key configured" : "SG.xxxxx..."} value={apiSettings.sendgrid_api_key} onChange={(e) => setApiSettings({...apiSettings, sendgrid_api_key: e.target.value})} className="font-mono" />
                    {apiSettings.sendgrid_configured && (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-600" />Configured
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveApiSettings} disabled={loading || !apiSettings.sendgrid_api_key}>
                    <Save className="h-4 w-4 mr-2" />
                    {loading ? 'Saving...' : 'Save API Key'}
                  </Button>
                  <Button variant="outline" onClick={handleTestEmail} disabled={testingEmail || !apiSettings.sendgrid_configured}>
                    <Key className="h-4 w-4 mr-2" />
                    {testingEmail ? 'Testing...' : 'Test Connection'}
                  </Button>
                </div>

                {emailTestResult && (
                  <div className={`p-3 rounded-md border flex items-start gap-2 ${emailTestResult.success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                    {emailTestResult.success ? <CheckCircle className="h-5 w-5 mt-0.5" /> : <XCircle className="h-5 w-5 mt-0.5" />}
                    <div>
                      <p className="font-medium">{emailTestResult.success ? 'Connection Successful' : 'Connection Failed'}</p>
                      <p className="text-sm">{emailTestResult.message}</p>
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">How to get SendGrid API Key:</h4>
                  <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                    <li>Sign up for free at <a href="https://signup.sendgrid.com/" target="_blank" rel="noopener noreferrer" className="underline">SendGrid</a></li>
                    <li>Navigate to Settings → API Keys</li>
                    <li>Click "Create API Key"</li>
                    <li>Give it Full Access or Mail Send permissions</li>
                    <li>Copy the key and paste it above</li>
                  </ol>
                  <p className="text-xs text-blue-700 mt-2">Free tier includes 100 emails/day!</p>
                </div>
              </CardContent>
            </Card>

            {/* Twilio SMS & WhatsApp Configuration */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Twilio SMS & WhatsApp</CardTitle>
                <CardDescription>Configure Twilio for SMS and WhatsApp notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Account SID</Label>
                    <p className="text-xs text-muted-foreground mb-2">Your Twilio Account SID</p>
                    <Input 
                      type="text" 
                      placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 
                      value={twilioSettings.account_sid} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, account_sid: e.target.value})} 
                      className="font-mono text-sm"
                    />
                  </div>
                  <div>
                    <Label>Auth Token</Label>
                    <p className="text-xs text-muted-foreground mb-2">Your Twilio Auth Token</p>
                    <Input 
                      type="password" 
                      placeholder={twilioSettings.twilio_configured ? "Token configured" : "Your auth token"} 
                      value={twilioSettings.auth_token} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, auth_token: e.target.value})} 
                      className="font-mono text-sm"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Phone Number (SMS)</Label>
                    <p className="text-xs text-muted-foreground mb-2">Your Twilio phone number for SMS</p>
                    <Input 
                      type="text" 
                      placeholder="+1234567890" 
                      value={twilioSettings.phone_number} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, phone_number: e.target.value})} 
                      className="font-mono"
                    />
                  </div>
                  <div>
                    <Label>WhatsApp Number (Optional)</Label>
                    <p className="text-xs text-muted-foreground mb-2">Twilio WhatsApp sandbox number</p>
                    <Input 
                      type="text" 
                      placeholder="+14155238886" 
                      value={twilioSettings.whatsapp_number} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, whatsapp_number: e.target.value})} 
                      className="font-mono"
                    />
                  </div>
                </div>

                {twilioSettings.twilio_configured && (
                  <Badge variant="outline" className="flex items-center gap-1 w-fit">
                    <CheckCircle className="h-3 w-3 text-green-600" />
                    Twilio Configured
                  </Badge>
                )}

                <div className="flex gap-2">
                  <Button onClick={handleSaveTwilioSettings} disabled={loading || !twilioSettings.account_sid || !twilioSettings.auth_token}>
                    <Save className="h-4 w-4 mr-2" />
                    {loading ? 'Saving...' : 'Save Twilio Settings'}
                  </Button>
                  <Button variant="outline" onClick={handleTestTwilio} disabled={testingTwilio || !twilioSettings.twilio_configured}>
                    <Key className="h-4 w-4 mr-2" />
                    {testingTwilio ? 'Testing...' : 'Test Connection'}
                  </Button>
                </div>

                {twilioTestResult && (
                  <div className={`p-3 rounded-md border flex items-start gap-2 ${twilioTestResult.success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                    {twilioTestResult.success ? <CheckCircle className="h-5 w-5 mt-0.5" /> : <XCircle className="h-5 w-5 mt-0.5" />}
                    <div>
                      <p className="font-medium">{twilioTestResult.success ? 'Twilio Connection Successful' : 'Connection Failed'}</p>
                      <p className="text-sm">{twilioTestResult.message}</p>
                      {twilioTestResult.account_sid && (
                        <p className="text-xs mt-1">Account: {twilioTestResult.account_sid}</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Test SMS & WhatsApp */}
                {twilioSettings.twilio_configured && (
                  <div className="border-t pt-6 space-y-6">
                    <h3 className="font-semibold text-lg">Test Messaging</h3>
                    
                    {/* Test SMS */}
                    <div className="space-y-3">
                      <Label className="text-base">Test SMS</Label>
                      <p className="text-xs text-muted-foreground">Send a test SMS to verify your configuration</p>
                      <div className="flex gap-2">
                        <Input 
                          type="tel" 
                          placeholder="+1234567890 (with country code)" 
                          value={testSMSPhone} 
                          onChange={(e) => setTestSMSPhone(e.target.value)} 
                          className="flex-1"
                        />
                        <Button 
                          onClick={handleTestSMS} 
                          disabled={sendingSMS || !testSMSPhone}
                          variant="outline"
                        >
                          {sendingSMS ? 'Sending...' : 'Send Test SMS'}
                        </Button>
                      </div>
                      {smsTestResult && (
                        <div className={`p-3 rounded-md border flex items-start gap-2 ${smsTestResult.success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                          {smsTestResult.success ? <CheckCircle className="h-5 w-5 mt-0.5" /> : <XCircle className="h-5 w-5 mt-0.5" />}
                          <div>
                            <p className="font-medium">{smsTestResult.success ? 'SMS Sent Successfully' : 'SMS Failed'}</p>
                            <p className="text-sm">{smsTestResult.message}</p>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Test WhatsApp */}
                    {twilioSettings.whatsapp_number && (
                      <div className="space-y-3">
                        <Label className="text-base">Test WhatsApp</Label>
                        <p className="text-xs text-muted-foreground">Send a test WhatsApp message (Note: Recipient must join your sandbox first)</p>
                        <div className="flex gap-2">
                          <Input 
                            type="tel" 
                            placeholder="whatsapp:+1234567890 (with country code)" 
                            value={testWhatsAppPhone} 
                            onChange={(e) => setTestWhatsAppPhone(e.target.value)} 
                            className="flex-1"
                          />
                          <Button 
                            onClick={handleTestWhatsApp} 
                            disabled={sendingWhatsApp || !testWhatsAppPhone}
                            variant="outline"
                          >
                            {sendingWhatsApp ? 'Sending...' : 'Send Test WhatsApp'}
                          </Button>
                        </div>
                        {whatsappTestResult && (
                          <div className={`p-3 rounded-md border flex items-start gap-2 ${whatsappTestResult.success ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
                            {whatsappTestResult.success ? <CheckCircle className="h-5 w-5 mt-0.5" /> : <XCircle className="h-5 w-5 mt-0.5" />}
                            <div>
                              <p className="font-medium">{whatsappTestResult.success ? 'WhatsApp Sent Successfully' : 'WhatsApp Failed'}</p>
                              <p className="text-sm">{whatsappTestResult.message}</p>
                            </div>
                          </div>
                        )}
                        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                          <p className="text-xs text-amber-800">
                            <strong>WhatsApp Sandbox Note:</strong> For testing, recipients must first send a join code to your WhatsApp sandbox number. 
                            Find your join code in Twilio Console → Messaging → Try it out → Send a WhatsApp message.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <Separator />

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-medium text-purple-900 mb-2">How to get Twilio Credentials:</h4>
                  <ol className="list-decimal list-inside text-sm text-purple-800 space-y-1">
                    <li>Sign up for free at <a href="https://www.twilio.com/try-twilio" target="_blank" rel="noopener noreferrer" className="underline">Twilio</a> (Get $15 credit)</li>
                    <li>Go to Console Dashboard</li>
                    <li>Copy your Account SID and Auth Token</li>
                    <li>Purchase a phone number ($1/month)</li>
                    <li>For WhatsApp: Go to Messaging → Try WhatsApp</li>
                  </ol>
                  <p className="text-xs text-purple-700 mt-2">Free trial includes $15 credit. SMS: ~$0.0075/msg, WhatsApp: ~$0.005/msg</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* GDPR & Privacy Tab */}
        <TabsContent value="gdpr">
          <div className="space-y-6">
            {/* Data Export */}
            <Card>
              <CardHeader>
                <CardTitle>Data Export</CardTitle>
                <CardDescription>Download all your personal data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Request a complete export of all your personal data stored in the system. This includes your profile, tasks, time entries, audit logs, and more.
                </p>
                
                <Button 
                  onClick={async () => {
                    try {
                      setExportingData(true);
                      const response = await axios.get(`${API}/gdpr/export-data`, {
                        headers: { Authorization: `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                      });
                      
                      // Create and download JSON file
                      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `my-data-export-${new Date().toISOString().split('T')[0]}.json`;
                      a.click();
                      
                      setMessage({ type: 'success', text: 'Data exported successfully!' });
                    } catch (err) {
                      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to export data' });
                    } finally {
                      setExportingData(false);
                    }
                  }}
                  disabled={exportingData}
                >
                  {exportingData ? 'Exporting...' : 'Export My Data'}
                </Button>
              </CardContent>
            </Card>

            {/* Consent Management */}
            <Card>
              <CardHeader>
                <CardTitle>Consent Management</CardTitle>
                <CardDescription>Manage your data processing consents</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium text-sm">Marketing Communications</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Receive product updates and promotional emails
                      </p>
                    </div>
                    <Switch
                      checked={gdprConsents.marketing}
                      onCheckedChange={async (checked) => {
                        try {
                          await axios.post(`${API}/gdpr/consents`, {
                            marketing: checked,
                            analytics: gdprConsents.analytics,
                            third_party: gdprConsents.third_party
                          }, {
                            headers: { Authorization: `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                          });
                          setGdprConsents({ ...gdprConsents, marketing: checked });
                          setMessage({ type: 'success', text: 'Consent updated' });
                        } catch (err) {
                          setMessage({ type: 'error', text: 'Failed to update consent' });
                        }
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium text-sm">Analytics & Performance</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Help us improve by sharing usage analytics
                      </p>
                    </div>
                    <Switch
                      checked={gdprConsents.analytics}
                      onCheckedChange={async (checked) => {
                        try {
                          await axios.post(`${API}/gdpr/consents`, {
                            marketing: gdprConsents.marketing,
                            analytics: checked,
                            third_party: gdprConsents.third_party
                          }, {
                            headers: { Authorization: `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                          });
                          setGdprConsents({ ...gdprConsents, analytics: checked });
                          setMessage({ type: 'success', text: 'Consent updated' });
                        } catch (err) {
                          setMessage({ type: 'error', text: 'Failed to update consent' });
                        }
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium text-sm">Third-Party Integrations</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Share data with integrated third-party services
                      </p>
                    </div>
                    <Switch
                      checked={gdprConsents.third_party}
                      onCheckedChange={async (checked) => {
                        try {
                          await axios.post(`${API}/gdpr/consents`, {
                            marketing: gdprConsents.marketing,
                            analytics: gdprConsents.analytics,
                            third_party: checked
                          }, {
                            headers: { Authorization: `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                          });
                          setGdprConsents({ ...gdprConsents, third_party: checked });
                          setMessage({ type: 'success', text: 'Consent updated' });
                        } catch (err) {
                          setMessage({ type: 'error', text: 'Failed to update consent' });
                        }
                      }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Delete Account */}
            <Card className="border-red-200 dark:border-red-800">
              <CardHeader>
                <CardTitle className="text-red-600 dark:text-red-400">Delete Account</CardTitle>
                <CardDescription>Permanently delete your account and all associated data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert className="bg-red-50 border-red-200">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    <strong>Warning:</strong> This action cannot be undone. All your data will be permanently deleted, except for audit logs which are retained for compliance purposes.
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    When you delete your account:
                  </p>
                  <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                    <li>Your profile and personal data will be deleted</li>
                    <li>Your tasks and time entries will be anonymized</li>
                    <li>You will lose access to all organization resources</li>
                    <li>Audit logs will be retained (anonymized) for compliance</li>
                  </ul>
                </div>
                
                <Button 
                  variant="destructive"
                  onClick={async () => {
                    if (!window.confirm('Are you absolutely sure? This action cannot be undone. Type DELETE to confirm.')) {
                      return;
                    }
                    
                    const confirmation = prompt('Type DELETE to confirm account deletion:');
                    if (confirmation !== 'DELETE') {
                      alert('Account deletion cancelled.');
                      return;
                    }
                    
                    try {
                      setDeletingAccount(true);
                      await axios.delete(`${API}/gdpr/delete-account`, {
                        headers: { Authorization: `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}` }
                      });
                      
                      alert('Your account has been deleted. You will now be logged out.');
                      // Logout user
                      localStorage.removeItem('token');
                      localStorage.removeItem('access_token');
                      window.location.href = '/login';
                    } catch (err) {
                      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to delete account' });
                    } finally {
                      setDeletingAccount(false);
                    }
                  }}
                  disabled={deletingAccount}
                >
                  {deletingAccount ? 'Deleting...' : 'Delete My Account'}
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Organization Tab */}
        {(isAdmin() || isDeveloper()) && (
          <TabsContent value="organization">
            <Card>
              <CardHeader>
                <CardTitle>Organization Settings</CardTitle>
                <CardDescription>Manage organization-wide settings</CardDescription>
              </CardHeader>
              <CardContent>
                <Alert className="bg-amber-50 border-amber-200">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  <AlertDescription className="text-amber-800">
                    Organization settings are coming soon. This section will include company logo upload, working hours configuration, holiday calendar, and default role settings.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default EnhancedSettingsPage;