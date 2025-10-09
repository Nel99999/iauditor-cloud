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

  const handleSaveAppearance = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/theme`, appearanceSettings);
      showMessage('success', 'Appearance settings saved!');
      // Apply font size immediately
      applyFontSize(appearanceSettings.font_size);
      applyDensity(appearanceSettings.view_density);
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save appearance settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveRegional = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/regional`, regionalSettings);
      showMessage('success', 'Regional settings saved!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save regional settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePrivacy = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/privacy`, privacySettings);
      showMessage('success', 'Privacy settings saved!');
    } catch (err) {
      showMessage('error', err.response?.data?.detail || 'Failed to save privacy settings');
    } finally {
      setLoading(false);
    }
  };

  const applyFontSize = (size) => {
    const root = document.documentElement;
    switch(size) {
      case 'small':
        root.style.fontSize = '14px'; // -2px from default 16px
        break;
      case 'large':
        root.style.fontSize = '18px'; // +2px from default 16px
        break;
      default:
        root.style.fontSize = '16px'; // medium
    }
  };

  const applyDensity = (density) => {
    const root = document.documentElement;
    root.classList.remove('density-compact', 'density-comfortable', 'density-spacious');
    root.classList.add(`density-${density}`);
  };

  useEffect(() => {
    if (appearanceSettings.font_size) {
      applyFontSize(appearanceSettings.font_size);
    }
    if (appearanceSettings.view_density) {
      applyDensity(appearanceSettings.view_density);
    }
  }, [appearanceSettings.font_size, appearanceSettings.view_density]);

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
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8">
          <TabsTrigger value="profile" className="gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Shield className="h-4 w-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="appearance" className="gap-2">
            <Palette className="h-4 w-4" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="regional" className="gap-2">
            <Globe className="h-4 w-4" />
            Regional
          </TabsTrigger>
          <TabsTrigger value="privacy" className="gap-2">
            <LockIcon className="h-4 w-4" />
            Privacy
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          {(user?.role === 'developer' || user?.role === 'master' || user?.role === 'admin') && (
            <TabsTrigger value="api" className="gap-2">
              <Key className="h-4 w-4" />
              API
            </TabsTrigger>
          )}
          <TabsTrigger value="organization" className="gap-2">
            <Building2 className="h-4 w-4" />
            Org
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

        {/* Appearance Tab */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>Customize how the application looks and feels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select value={appearanceSettings.theme} onValueChange={(value) => setAppearanceSettings({...appearanceSettings, theme: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto (System)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="accent-color">Accent Color</Label>
                  <div className="flex gap-2">
                    <Input
                      id="accent-color"
                      type="color"
                      value={appearanceSettings.accent_color}
                      onChange={(e) => setAppearanceSettings({...appearanceSettings, accent_color: e.target.value})}
                      className="w-20 h-10"
                    />
                    <Input
                      type="text"
                      value={appearanceSettings.accent_color}
                      onChange={(e) => setAppearanceSettings({...appearanceSettings, accent_color: e.target.value})}
                      className="font-mono"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">Choose your primary accent color</p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="font-size">Font Size</Label>
                  <Select value={appearanceSettings.font_size} onValueChange={(value) => setAppearanceSettings({...appearanceSettings, font_size: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="small">Small (14px) - Compact view</SelectItem>
                      <SelectItem value="medium">Medium (16px) - Default</SelectItem>
                      <SelectItem value="large">Large (18px) - Better readability</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">Current: {appearanceSettings.font_size === 'small' ? '14px (-2)' : appearanceSettings.font_size === 'large' ? '18px (+2)' : '16px (default)'}</p>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label htmlFor="density">View Density</Label>
                  <Select value={appearanceSettings.view_density} onValueChange={(value) => setAppearanceSettings({...appearanceSettings, view_density: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="compact">Compact - More content, less spacing</SelectItem>
                      <SelectItem value="comfortable">Comfortable - Balanced (Default)</SelectItem>
                      <SelectItem value="spacious">Spacious - More breathing room</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">Controls spacing between elements</p>
                </div>
              </div>

              <Button onClick={handleSaveAppearance} className="gap-2" disabled={loading}>
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Appearance'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Regional Tab */}
        <TabsContent value="regional">
          <Card>
            <CardHeader>
              <CardTitle>Regional Settings</CardTitle>
              <CardDescription>Set your language, timezone, and formatting preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select value={regionalSettings.language} onValueChange={(value) => setRegionalSettings({...regionalSettings, language: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                      <SelectItem value="zh">中文</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={regionalSettings.timezone} onValueChange={(value) => setRegionalSettings({...regionalSettings, timezone: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time (US)</SelectItem>
                      <SelectItem value="America/Chicago">Central Time (US)</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time (US)</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time (US)</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Asia/Dubai">Dubai</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                      <SelectItem value="Africa/Johannesburg">Johannesburg</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="date-format">Date Format</Label>
                    <Select value={regionalSettings.date_format} onValueChange={(value) => setRegionalSettings({...regionalSettings, date_format: value})}>
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

                  <div className="space-y-2">
                    <Label htmlFor="time-format">Time Format</Label>
                    <Select value={regionalSettings.time_format} onValueChange={(value) => setRegionalSettings({...regionalSettings, time_format: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="12h">12 Hour</SelectItem>
                        <SelectItem value="24h">24 Hour</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={regionalSettings.currency} onValueChange={(value) => setRegionalSettings({...regionalSettings, currency: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD ($)</SelectItem>
                      <SelectItem value="EUR">EUR (€)</SelectItem>
                      <SelectItem value="GBP">GBP (£)</SelectItem>
                      <SelectItem value="ZAR">ZAR (R)</SelectItem>
                      <SelectItem value="JPY">JPY (¥)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={handleSaveRegional} className="gap-2" disabled={loading}>
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Regional Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Tab */}
        <TabsContent value="privacy">
          <Card>
            <CardHeader>
              <CardTitle>Privacy Settings</CardTitle>
              <CardDescription>Control your privacy and visibility preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="profile-visibility">Profile Visibility</Label>
                  <Select value={privacySettings.profile_visibility} onValueChange={(value) => setPrivacySettings({...privacySettings, profile_visibility: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="organization">Organization Only</SelectItem>
                      <SelectItem value="team">My Team Only</SelectItem>
                      <SelectItem value="private">Private</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">Who can see your profile</p>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Show Activity Status</Label>
                    <p className="text-sm text-muted-foreground">
                      Let others see when you're active
                    </p>
                  </div>
                  <Switch
                    checked={privacySettings.show_activity_status}
                    onCheckedChange={(checked) =>
                      setPrivacySettings({ ...privacySettings, show_activity_status: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Show Last Seen</Label>
                    <p className="text-sm text-muted-foreground">
                      Display your last seen time
                    </p>
                  </div>
                  <Switch
                    checked={privacySettings.show_last_seen}
                    onCheckedChange={(checked) =>
                      setPrivacySettings({ ...privacySettings, show_last_seen: checked })
                    }
                  />
                </div>
              </div>

              <Button onClick={handleSavePrivacy} className="gap-2" disabled={loading}>
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Privacy Settings'}
              </Button>
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