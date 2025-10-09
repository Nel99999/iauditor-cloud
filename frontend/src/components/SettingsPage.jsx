import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PhoneInput from 'react-phone-number-input';
import 'react-phone-number-input/style.css';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Settings, User, Shield, Bell, Building2, Save, Upload, Key, CheckCircle, XCircle, Palette, Globe, Lock as LockIcon } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = () => {
  const { user, setUser } = useAuth();
  const [profileData, setProfileData] = useState({ name: '', phone: '', bio: '' });
  const [passwordData, setPasswordData] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: false,
    weeklyReports: true,
    marketingEmails: false,
  });
  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: 'light',
    accent_color: '#6366f1',
    font_size: 'medium',
    view_density: 'comfortable'
  });
  const [regionalSettings, setRegionalSettings] = useState({
    language: 'en',
    timezone: 'UTC',
    date_format: 'MM/DD/YYYY',
    time_format: '12h',
    currency: 'USD'
  });
  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: 'organization',
    show_activity_status: true,
    show_last_seen: true
  });
  const [apiSettings, setApiSettings] = useState({
    sendgrid_api_key: '',
    sendgrid_configured: false
  });
  const [testingEmail, setTestingEmail] = useState(false);
  const [emailTestResult, setEmailTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadSettings();
    loadApiSettings();
    loadAppearanceSettings();
    loadRegionalSettings();
    loadPrivacySettings();
    if (user) {
      setProfileData({ name: user.name || '', phone: user.phone || '', bio: user.bio || '' });
    }
  }, [user]);

  const loadApiSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings/email`);
      setApiSettings(response.data);
    } catch (err) {
      console.error('Failed to load API settings:', err);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await axios.get(`${API}/users/settings`);
      const data = response.data;
      setSettings({
        emailNotifications: data.email_notifications,
        pushNotifications: data.push_notifications,
        weeklyReports: data.weekly_reports,
        marketingEmails: data.marketing_emails,
      });
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const loadAppearanceSettings = async () => {
    try {
      const response = await axios.get(`${API}/users/theme`);
      setAppearanceSettings(response.data);
    } catch (err) {
      console.error('Failed to load appearance settings:', err);
    }
  };

  const loadRegionalSettings = async () => {
    try {
      const response = await axios.get(`${API}/users/regional`);
      setRegionalSettings(response.data);
    } catch (err) {
      console.error('Failed to load regional settings:', err);
    }
  };

  const loadPrivacySettings = async () => {
    try {
      const response = await axios.get(`${API}/users/privacy`);
      setPrivacySettings(response.data);
    } catch (err) {
      console.error('Failed to load privacy settings:', err);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.put(`${API}/users/profile`, {
        name: profileData.name,
        phone: profileData.phone,
        bio: profileData.bio,
      });
      // Update user context
      setUser({ ...user, name: profileData.name, phone: profileData.phone, bio: profileData.bio });
      showMessage('success', 'Profile updated successfully!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePassword = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      showMessage('error', 'New passwords do not match');
      return;
    }
    if (passwordData.new_password.length < 6) {
      showMessage('error', 'Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    try {
      await axios.put(`${API}/users/password`, {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      showMessage('success', 'Password updated successfully!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to update password');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotifications = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/settings`, {
        email_notifications: settings.emailNotifications,
        push_notifications: settings.pushNotifications,
        weekly_reports: settings.weeklyReports,
        marketing_emails: settings.marketingEmails,
      });
      showMessage('success', 'Notification preferences saved!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/settings/email`, {
        sendgrid_api_key: apiSettings.sendgrid_api_key
      });
      showMessage('success', 'SendGrid API key saved successfully!');
      loadApiSettings();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save API key');
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
      setEmailTestResult({ 
        success: false, 
        message: err.response?.data?.detail || 'Test failed' 
      });
    } finally {
      setTestingEmail(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      showMessage('error', 'Please upload an image file');
      return;
    }
    
    if (file.size > 2 * 1024 * 1024) {
      showMessage('error', 'File size must be less than 2MB');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API}/users/profile/picture`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      // Update user context with new picture URL and add timestamp to force refresh
      const newPictureUrl = `${BACKEND_URL}${response.data.picture_url}?t=${Date.now()}`;
      setUser({ ...user, picture: newPictureUrl });
      showMessage('success', 'Profile picture updated!');
      
      // Force re-render by updating state
      window.location.reload();
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to upload photo');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="space-y-6">
      {message.text && (
        <div className={`p-4 rounded-md ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
          {message.text}
        </div>
      )}

      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Settings
        </h1>
        <p className="text-slate-600 dark:text-slate-400">
          Manage your account settings and preferences
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile" className="gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Shield className="h-4 w-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          {(user?.role === 'developer' || user?.role === 'master' || user?.role === 'admin') && (
            <TabsTrigger value="api" className="gap-2">
              <Key className="h-4 w-4" />
              API Settings
            </TabsTrigger>
          )}
          <TabsTrigger value="organization" className="gap-2">
            <Building2 className="h-4 w-4" />
            Organization
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-6">
                <Avatar className="h-20 w-20">
                  <AvatarImage src={user?.picture} alt={user?.name} />
                  <AvatarFallback>{getInitials(user?.name || 'U')}</AvatarFallback>
                </Avatar>
                <div>
                  <input
                    type="file"
                    id="photo-upload"
                    className="hidden"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                  />
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => document.getElementById('photo-upload').click()}
                    disabled={loading}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Change Photo
                  </Button>
                  <p className="text-sm text-muted-foreground mt-2">
                    JPG, PNG or GIF. Max 2MB
                  </p>
                </div>
              </div>

              <Separator />

              <form onSubmit={handleSaveProfile} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input 
                      id="name" 
                      value={profileData.name}
                      onChange={(e) => setProfileData({...profileData, name: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" value={user?.email} disabled />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <PhoneInput
                    id="phone"
                    international
                    defaultCountry="ZA"
                    value={profileData.phone}
                    onChange={(value) => setProfileData({...profileData, phone: value || ''})}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                    placeholder="+27 XX XXX XXXX"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Input 
                    id="bio" 
                    value={profileData.bio}
                    onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                    placeholder="Optional"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <div className="flex items-center gap-2">
                    <Input id="role" value={user?.role} disabled className="max-w-xs" />
                    <Badge variant="outline" className="capitalize">
                      {user?.role}
                    </Badge>
                  </div>
                </div>

                <Button type="submit" className="gap-2" disabled={loading}>
                  <Save className="h-4 w-4" />
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Manage your password and security preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-sm font-medium mb-4">Change Password</h3>
                <form onSubmit={handleSavePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <Input 
                      id="current-password" 
                      type="password"
                      value={passwordData.current_password}
                      onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <Input 
                      id="new-password" 
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <Input 
                      id="confirm-password" 
                      type="password"
                      value={passwordData.confirm_password}
                      onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                    />
                  </div>
                  <Button type="submit" className="gap-2" disabled={loading}>
                    <Save className="h-4 w-4" />
                    {loading ? 'Updating...' : 'Update Password'}
                  </Button>
                </form>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-medium mb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Enable two-factor authentication</p>
                    <p className="text-xs text-muted-foreground">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                  <Badge variant="outline">Coming Soon</Badge>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-medium mb-4">Active Sessions</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="text-sm font-medium">Current Session</p>
                      <p className="text-xs text-muted-foreground">Last active: Now</p>
                    </div>
                    <Badge>Active</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Choose what notifications you want to receive</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive email about account activity
                    </p>
                  </div>
                  <Switch
                    checked={settings.emailNotifications}
                    onCheckedChange={(checked) =>
                      setSettings({ ...settings, emailNotifications: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive push notifications on your devices
                    </p>
                  </div>
                  <Switch
                    checked={settings.pushNotifications}
                    onCheckedChange={(checked) =>
                      setSettings({ ...settings, pushNotifications: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Weekly Reports</Label>
                    <p className="text-sm text-muted-foreground">
                      Get a weekly summary of your operations
                    </p>
                  </div>
                  <Switch
                    checked={settings.weeklyReports}
                    onCheckedChange={(checked) =>
                      setSettings({ ...settings, weeklyReports: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Marketing Emails</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive emails about new features and updates
                    </p>
                  </div>
                  <Switch
                    checked={settings.marketingEmails}
                    onCheckedChange={(checked) =>
                      setSettings({ ...settings, marketingEmails: checked })
                    }
                  />
                </div>
              </div>

              <Button onClick={handleSaveNotifications} className="gap-2" disabled={loading}>
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Preferences'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Settings Tab */}
        <TabsContent value="api">
          <Card>
            <CardHeader>
              <CardTitle>API Configuration</CardTitle>
              <CardDescription>Manage third-party API keys for email and other integrations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="sendgrid-key">SendGrid API Key</Label>
                  <p className="text-xs text-muted-foreground mb-2">
                    Required for sending invitation emails. Get your API key from{' '}
                    <a href="https://app.sendgrid.com/settings/api_keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      SendGrid Dashboard
                    </a>
                  </p>
                  <div className="flex gap-2">
                    <Input
                      id="sendgrid-key"
                      type="password"
                      placeholder={apiSettings.sendgrid_configured ? "API key configured (hidden)" : "SG.xxxxx..."}
                      value={apiSettings.sendgrid_api_key}
                      onChange={(e) => setApiSettings({ ...apiSettings, sendgrid_api_key: e.target.value })}
                      className="font-mono text-sm"
                    />
                    {apiSettings.sendgrid_configured && (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        Configured
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveApiSettings} disabled={loading || !apiSettings.sendgrid_api_key}>
                    <Save className="h-4 w-4 mr-2" />
                    {loading ? 'Saving...' : 'Save API Key'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={handleTestEmail} 
                    disabled={testingEmail || !apiSettings.sendgrid_configured}
                  >
                    <Key className="h-4 w-4 mr-2" />
                    {testingEmail ? 'Testing...' : 'Test Connection'}
                  </Button>
                </div>

                {emailTestResult && (
                  <div className={`p-3 rounded-md border flex items-start gap-2 ${
                    emailTestResult.success 
                      ? 'bg-green-50 border-green-200 text-green-800' 
                      : 'bg-red-50 border-red-200 text-red-800'
                  }`}>
                    {emailTestResult.success ? (
                      <CheckCircle className="h-5 w-5 mt-0.5" />
                    ) : (
                      <XCircle className="h-5 w-5 mt-0.5" />
                    )}
                    <div>
                      <p className="font-medium">
                        {emailTestResult.success ? 'Connection Successful' : 'Connection Failed'}
                      </p>
                      <p className="text-sm">{emailTestResult.message}</p>
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">How to get SendGrid API Key:</h4>
                <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                  <li>Sign up for free at <a href="https://signup.sendgrid.com/" target="_blank" rel="noopener noreferrer" className="underline">SendGrid</a></li>
                  <li>Navigate to Settings → API Keys</li>
                  <li>Click "Create API Key"</li>
                  <li>Give it Full Access or Mail Send permissions</li>
                  <li>Copy the key and paste it above</li>
                </ol>
                <p className="text-xs text-blue-700 mt-2">
                  Free tier includes 100 emails/day - perfect for testing!
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Organization Tab */}
        <TabsContent value="organization">
          <Card>
            <CardHeader>
              <CardTitle>Organization Settings</CardTitle>
              <CardDescription>Manage organization-wide settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Organization Name</Label>
                <Input defaultValue="Test Organization" disabled />
                <p className="text-xs text-muted-foreground">Contact admin to change organization details</p>
              </div>

              <div className="space-y-2">
                <Label>Industry</Label>
                <Input defaultValue="Manufacturing" disabled />
              </div>

              <div className="space-y-2">
                <Label>Company Size</Label>
                <Input defaultValue="50-200 employees" disabled />
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-medium mb-2">Danger Zone</h3>
                <div className="border border-red-200 rounded-lg p-4 space-y-2">
                  <p className="text-sm text-red-600">Delete Organization</p>
                  <p className="text-xs text-muted-foreground">
                    This action cannot be undone. This will permanently delete your organization
                    and all associated data.
                  </p>
                  <Button variant="destructive" size="sm" disabled>
                    Delete Organization
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SettingsPage;