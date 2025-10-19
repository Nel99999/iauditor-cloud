// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '@/hooks/usePermissions';
import { PermissionGuard } from '@/components/PermissionGuard';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  User, Shield, Key, Upload, Save, CheckCircle, Lock, 
  AlertTriangle, Building2, Users, Activity, Clock, 
  Smartphone, Mail, Webhook, Download, Trash2, ExternalLink,
  Globe, Laptop, MapPin
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ModernSettingsPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const { isDeveloperOrMaster, hasPermission, userPermissions, userRole } = usePermissions();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  // Profile state
  const [profileData, setProfileData] = useState({ name: '', phone: '' });
  const [orgContext, setOrgContext] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  // Sidebar Preferences state
  const [sidebarPrefs, setSidebarPrefs] = useState({
    default_mode: 'expanded',
    hover_expand_enabled: true,
    auto_collapse_enabled: false,
    inactivity_timeout: 10,
    context_aware_enabled: true,
    collapse_after_navigation: false
  });

  // Security state
  const [passwordData, setPasswordData] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);
  const [mfaEnabled, setMfaEnabled] = useState(false);

  // Admin state (Master/Developer only)
  const [apiSettings, setApiSettings] = useState({
    sendgrid_api_key: '',
    sendgrid_configured: false,
    sendgrid_from_email: '',
    sendgrid_from_name: ''
  });
  const [twilioSettings, setTwilioSettings] = useState({
    account_sid: '',
    auth_token: '',
    phone_number: '',
    whatsapp_number: '',
    twilio_configured: false
  });
  const [webhookCount, setWebhookCount] = useState(0);
  const [gdprConsents, setGdprConsents] = useState({
    marketing: false,
    analytics: false,
    third_party: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load profile data
      const profileRes = await axios.get(`${API}/users/me`);
      setProfileData({
        name: profileRes.data.name || '',
        phone: profileRes.data.phone || ''
      });
      setMfaEnabled(profileRes.data.mfa_enabled || false);

      // Load organizational context (NEW endpoint - will create)
      try {
        const orgContextRes = await axios.get(`${API}/users/me/org-context`);
        setOrgContext(orgContextRes.data);
      } catch (err) {
        console.log('Org context not available yet');
      }

      // Load recent activity (NEW endpoint - will create)
      try {
        const activityRes = await axios.get(`${API}/users/me/recent-activity?limit=5`);
        setRecentActivity(activityRes.data || []);
      } catch (err) {
        console.log('Recent activity not available yet');
      }

      // Load active sessions (NEW endpoint - will create)
      try {
        const sessionsRes = await axios.get(`${API}/auth/sessions`);
        setActiveSessions(sessionsRes.data || []);
      } catch (err) {
        console.log('Sessions not available yet');
        setActiveSessions([]);
      }

      // Load security events from audit logs
      try {
        const eventsRes = await axios.get(`${API}/audit/logs?user_id=${user?.id}&limit=10`);
        setSecurityEvents(eventsRes.data.logs || []);
      } catch (err) {
        console.log('Security events not available');
      }

      // Load sidebar preferences
      try {
        const sidebarRes = await axios.get(`${API}/users/sidebar-preferences`);
        setSidebarPrefs(sidebarRes.data || sidebarPrefs);
      } catch (err) {
        console.log('Sidebar preferences not available, using defaults');
      }

      // Load admin settings (only for Master/Developer)
      if (isDeveloperOrMaster()) {
        try {
          const [emailRes, twilioRes, webhooksRes, consentsRes] = await Promise.all([
            axios.get(`${API}/settings/email`),
            axios.get(`${API}/sms/settings`),
            axios.get(`${API}/webhooks`),
            axios.get(`${API}/gdpr/consent-status`)
          ]);
          
          setApiSettings(emailRes.data || {});
          setTwilioSettings(twilioRes.data || {});
          setWebhookCount(webhooksRes.data?.webhooks?.length || 0);
          setGdprConsents(consentsRes.data || {});
        } catch (err) {
          console.log('Admin data load error:', err);
        }
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e: any) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/users/profile/picture`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast({
        title: 'Success',
        description: 'Photo uploaded successfully!',
      });
      
      // Reload page to show new photo
      window.location.reload();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to upload photo',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.put(`${API}/users/profile`, profileData);
      toast({
        title: 'Success',
        description: 'Profile updated successfully!',
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to update profile',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: any) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast({
        title: 'Error',
        description: 'Passwords do not match',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/auth/change-password`, {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      toast({
        title: 'Success',
        description: 'Password changed successfully!',
      });
      
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to change password',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    if (!confirm('Revoke this session? You will be logged out on that device.')) return;
    
    try {
      await axios.delete(`${API}/auth/sessions/${sessionId}`);
      toast({
        title: 'Success',
        description: 'Session revoked successfully',
      });
      loadData();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to revoke session',
        variant: 'destructive'
      });
    }
  };

  const handleSaveApiSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/settings/email`, apiSettings);
      toast({
        title: 'Success',
        description: 'Email settings saved successfully!',
      });
      loadData();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to save email settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    try {
      await axios.post(`${API}/settings/test-email`);
      toast({
        title: 'Success',
        description: 'Test email sent! Check your inbox.',
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to send test email',
        variant: 'destructive'
      });
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
      toast({
        title: 'Success',
        description: 'Twilio settings saved successfully!',
      });
      loadData();
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to save Twilio settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestTwilio = async () => {
    try {
      await axios.post(`${API}/sms/test-connection`);
      toast({
        title: 'Success',
        description: 'Twilio connection successful!',
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to connect to Twilio',
        variant: 'destructive'
      });
    }
  };

  const handleSaveSidebarPreferences = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/sidebar-preferences`, sidebarPrefs);
      toast({
        title: 'Success',
        description: 'Sidebar preferences saved! Refresh the page to see changes.',
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to save sidebar preferences',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      const response = await axios.get(`${API}/gdpr/export-data`);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `my-data-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      
      toast({
        title: 'Success',
        description: 'Data exported successfully!',
      });
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to export data',
        variant: 'destructive'
      });
    }
  };

  const handleDeleteAccount = async () => {
    const confirmation = prompt('Type DELETE to confirm account deletion:');
    if (confirmation !== 'DELETE') return;
    
    try {
      await axios.delete(`${API}/gdpr/delete-account`);
      toast({
        title: 'Account Deleted',
        description: 'Your account has been deleted.',
      });
      // Logout
      window.location.href = '/login';
    } catch (err: any) {
      toast({
        title: 'Error',
        description: 'Failed to delete account',
        variant: 'destructive'
      });
    }
  };

  // Calculate visible tab count
  const tabCount = isDeveloperOrMaster() ? 3 : 2;

  return (
    <ModernPageWrapper
      title="Settings"
      subtitle="Manage your account and preferences"
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className={`grid w-full grid-cols-${tabCount}`}>
          <TabsTrigger value="profile">
            <User className="h-4 w-4 mr-2" />
            My Profile & Role
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-2" />
            Security & Access
          </TabsTrigger>
          {isDeveloperOrMaster() && (
            <TabsTrigger value="admin">
              <Key className="h-4 w-4 mr-2" />
              Admin & Compliance
            </TabsTrigger>
          )}
        </TabsList>

        {/* TAB 1: MY PROFILE & ROLE */}
        <TabsContent value="profile" className="space-y-6">
          
          {/* Personal Information */}
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>Your account details and contact information</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-6">
                
                {/* Photo Upload */}
                <div className="flex items-center gap-6">
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
                  <div>
                    <Label htmlFor="photo" className="cursor-pointer">
                      <div className="flex items-center gap-2 px-4 py-2 border rounded-md hover:bg-slate-50 dark:hover:bg-slate-800">
                        <Upload className="h-4 w-4" />
                        Upload Photo
                      </div>
                    </Label>
                    <Input id="photo" type="file" accept="image/*" onChange={handlePhotoUpload} className="hidden" />
                    <p className="text-xs text-muted-foreground mt-1">JPG, PNG or GIF (max 2MB)</p>
                  </div>
                </div>

                <Separator />

                {/* Name and Phone */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input 
                      id="name" 
                      value={profileData.name} 
                      onChange={(e) => setProfileData({...profileData, name: e.target.value})} 
                      required 
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input 
                      id="phone" 
                      type="tel"
                      value={profileData.phone} 
                      onChange={(e) => setProfileData({...profileData, phone: e.target.value})} 
                    />
                  </div>
                </div>

                {/* Email (read-only) */}
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" value={user?.email || ''} disabled className="bg-muted" />
                  <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
                </div>

                <Button type="submit" disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Organizational Context */}
          <Card>
            <CardHeader>
              <CardTitle>Role & Organization</CardTitle>
              <CardDescription>Your position and responsibilities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              
              {/* Role & Level */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-muted/50 rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Current Role</p>
                  <Badge className="font-semibold capitalize">{user?.role || 'viewer'}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Hierarchy Level</p>
                  <p className="font-semibold">Level {userRole?.level || 10}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Permissions</p>
                  <p className="font-semibold">{userPermissions.length} of 49 assigned</p>
                </div>
              </div>

              {/* Organizational Position */}
              {orgContext && (
                <div className="space-y-3">
                  <Label>Position in Organization</Label>
                  <div className="p-3 border rounded-lg space-y-2">
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{orgContext.organization_name || 'Organization'}</span>
                    </div>
                    <div className="flex items-center gap-2 pl-6">
                      <span className="text-sm text-muted-foreground">└─</span>
                      <span className="text-sm font-medium">{orgContext.unit_name || 'Not assigned'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Manager & Team */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Direct Manager</p>
                  <p className="font-medium text-sm">{orgContext?.manager_name || 'None'}</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Team Members</p>
                  <p className="font-medium text-sm">{orgContext?.team_size || 0} people</p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => window.location.href = '/roles'}>
                  <Shield className="h-4 w-4 mr-2" />
                  View My Permissions
                </Button>
                {orgContext?.team_size > 0 && (
                  <Button variant="outline" size="sm" onClick={() => window.location.href = '/users'}>
                    <Users className="h-4 w-4 mr-2" />
                    View My Team
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          {recentActivity.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Your last 5 actions in the system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentActivity.map((activity, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-2 hover:bg-muted/50 rounded-lg">
                      <Activity className="h-4 w-4 text-muted-foreground mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.action}</p>
                        <p className="text-xs text-muted-foreground">
                          {activity.resource_type} • {new Date(activity.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="link" size="sm" className="mt-2" onClick={() => window.location.href = '/audit'}>
                  View Full Activity Log →
                </Button>
              </CardContent>
            </Card>
          )}

        </TabsContent>

        {/* TAB 2: SECURITY & ACCESS */}
        <TabsContent value="security" className="space-y-6">
          
          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>Update your password regularly for security</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <Label htmlFor="current_password">Current Password</Label>
                  <Input 
                    id="current_password" 
                    type="password" 
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                    required 
                  />
                </div>
                <div>
                  <Label htmlFor="new_password">New Password</Label>
                  <Input 
                    id="new_password" 
                    type="password" 
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                    required 
                  />
                </div>
                <div>
                  <Label htmlFor="confirm_password">Confirm New Password</Label>
                  <Input 
                    id="confirm_password" 
                    type="password" 
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                    required 
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Two-Factor Authentication */}
          <Card>
            <CardHeader>
              <CardTitle>Two-Factor Authentication</CardTitle>
              <CardDescription>Add an extra layer of security to your account</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">2FA Status</p>
                  <p className="text-sm text-muted-foreground">
                    {mfaEnabled ? 'Two-factor authentication is enabled' : 'Two-factor authentication is disabled'}
                  </p>
                </div>
                <Badge variant={mfaEnabled ? 'default' : 'secondary'}>
                  {mfaEnabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
              {!mfaEnabled && (
                <Button className="mt-4" onClick={() => window.location.href = '/mfa/setup'}>
                  <Shield className="h-4 w-4 mr-2" />
                  Setup 2FA
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Active Sessions */}
          <Card>
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>Manage devices where you're logged in</CardDescription>
            </CardHeader>
            <CardContent>
              {activeSessions.length === 0 ? (
                <Alert>
                  <Clock className="h-4 w-4" />
                  <AlertDescription>
                    Current session only. Session management feature coming soon.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-2">
                  {activeSessions.map((session, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Laptop className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-sm">{session.device || 'Unknown Device'}</p>
                          <p className="text-xs text-muted-foreground">
                            <MapPin className="h-3 w-3 inline mr-1" />
                            {session.location || 'Unknown'} • {session.last_active || 'Just now'}
                          </p>
                        </div>
                      </div>
                      {session.is_current ? (
                        <Badge variant="default">Current</Badge>
                      ) : (
                        <Button variant="outline" size="sm" onClick={() => handleRevokeSession(session.id)}>
                          Revoke
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Security Events */}
          {securityEvents.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Security Events</CardTitle>
                <CardDescription>Last 10 security-related activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {securityEvents.map((event, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-2 hover:bg-muted/50 rounded-lg">
                      <div className={`mt-0.5 ${event.result === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                        {event.result === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{event.action}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(event.created_at).toLocaleString()} • {event.context?.ip_address || 'Unknown IP'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

        </TabsContent>

        {/* TAB 3: ADMIN & COMPLIANCE (Master/Developer Only) */}
        {isDeveloperOrMaster() && (
          <TabsContent value="admin" className="space-y-6">
            
            {/* SendGrid Email Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>Email Configuration (SendGrid)</CardTitle>
                <CardDescription>Configure email sending for notifications and alerts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert className="bg-blue-50 border-blue-200">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-900">
                    <strong>Master & Developer Only:</strong> Email configuration affects the entire organization.
                  </AlertDescription>
                </Alert>

                <div>
                  <Label htmlFor="sendgrid_api_key">SendGrid API Key</Label>
                  <Input 
                    id="sendgrid_api_key"
                    type="password" 
                    placeholder={apiSettings.sendgrid_configured ? "API key configured" : "SG.xxxxx..."} 
                    value={apiSettings.sendgrid_api_key} 
                    onChange={(e) => setApiSettings({...apiSettings, sendgrid_api_key: e.target.value})} 
                    className="font-mono" 
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="from_email">From Email</Label>
                    <Input 
                      id="from_email"
                      type="email"
                      placeholder="noreply@company.com" 
                      value={apiSettings.sendgrid_from_email} 
                      onChange={(e) => setApiSettings({...apiSettings, sendgrid_from_email: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label htmlFor="from_name">From Name</Label>
                    <Input 
                      id="from_name"
                      placeholder="Company Name" 
                      value={apiSettings.sendgrid_from_name} 
                      onChange={(e) => setApiSettings({...apiSettings, sendgrid_from_name: e.target.value})} 
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveApiSettings} disabled={loading}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Configuration
                  </Button>
                  <Button variant="outline" onClick={handleTestEmail}>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Test Email
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Twilio SMS/WhatsApp Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>SMS & WhatsApp (Twilio)</CardTitle>
                <CardDescription>Configure SMS and WhatsApp notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert className="bg-blue-50 border-blue-200">
                  <Shield className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-900">
                    <strong>Master & Developer Only:</strong> Twilio configuration affects the entire organization.
                  </AlertDescription>
                </Alert>

                <div className="flex items-center gap-2 mb-4">
                  <Badge variant={twilioSettings.twilio_configured ? 'default' : 'secondary'}>
                    {twilioSettings.twilio_configured ? '✓ Configured' : 'Not Configured'}
                  </Badge>
                </div>

                <div>
                  <Label htmlFor="twilio_account_sid">Account SID</Label>
                  <Input 
                    id="twilio_account_sid"
                    type="text" 
                    placeholder={twilioSettings.twilio_configured ? twilioSettings.account_sid : "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"} 
                    value={twilioSettings.account_sid} 
                    onChange={(e) => setTwilioSettings({...twilioSettings, account_sid: e.target.value})} 
                    className="font-mono" 
                  />
                </div>

                <div>
                  <Label htmlFor="twilio_auth_token">Auth Token</Label>
                  <Input 
                    id="twilio_auth_token"
                    type="password" 
                    placeholder={twilioSettings.twilio_configured ? "Token configured" : "Your Twilio Auth Token"} 
                    value={twilioSettings.auth_token} 
                    onChange={(e) => setTwilioSettings({...twilioSettings, auth_token: e.target.value})} 
                    className="font-mono" 
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="twilio_phone_number">SMS Phone Number</Label>
                    <Input 
                      id="twilio_phone_number"
                      type="tel"
                      placeholder="+1234567890" 
                      value={twilioSettings.phone_number} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, phone_number: e.target.value})} 
                    />
                  </div>
                  <div>
                    <Label htmlFor="twilio_whatsapp_number">WhatsApp Number (Optional)</Label>
                    <Input 
                      id="twilio_whatsapp_number"
                      type="tel"
                      placeholder="+1234567890" 
                      value={twilioSettings.whatsapp_number} 
                      onChange={(e) => setTwilioSettings({...twilioSettings, whatsapp_number: e.target.value})} 
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveTwilioSettings} disabled={loading}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Configuration
                  </Button>
                  <Button variant="outline" onClick={handleTestTwilio} disabled={!twilioSettings.twilio_configured}>
                    <Smartphone className="h-4 w-4 mr-2" />
                    Test Connection
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Webhooks Dashboard */}
            <PermissionGuard 
              anyPermissions={['webhook.manage.organization']}
              minLevel={3}
              fallback="hide"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Webhook Integrations</CardTitle>
                  <CardDescription>Connect external services to system events</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Webhook className="h-8 w-8 text-muted-foreground" />
                      <div>
                        <p className="font-medium">Active Webhooks</p>
                        <p className="text-sm text-muted-foreground">{webhookCount} configured</p>
                      </div>
                    </div>
                    <Button variant="outline" onClick={() => window.location.href = '/webhooks'}>
                      Manage Webhooks
                      <ExternalLink className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </PermissionGuard>

            {/* GDPR & Data Privacy */}
            <Card>
              <CardHeader>
                <CardTitle>Data & Privacy</CardTitle>
                <CardDescription>Export your data or manage consents</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                {/* Data Export */}
                <div>
                  <Label>Export Your Data</Label>
                  <p className="text-sm text-muted-foreground mb-3">
                    Download all your personal data in JSON format
                  </p>
                  <Button variant="outline" onClick={handleExportData}>
                    <Download className="h-4 w-4 mr-2" />
                    Export My Data
                  </Button>
                </div>

                <Separator />

                {/* Consent Management */}
                <div>
                  <Label>Data Processing Consents</Label>
                  <div className="space-y-3 mt-3">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium text-sm">Analytics & Performance</p>
                        <p className="text-xs text-muted-foreground">Help us improve the platform</p>
                      </div>
                      <Switch 
                        checked={gdprConsents.analytics}
                        onCheckedChange={async (checked) => {
                          try {
                            await axios.put(`${API}/gdpr/consent`, {
                              ...gdprConsents,
                              analytics: checked
                            });
                            setGdprConsents({...gdprConsents, analytics: checked});
                            toast({ title: 'Consent updated' });
                          } catch (err) {
                            toast({ title: 'Error', description: 'Failed to update', variant: 'destructive' });
                          }
                        }}
                      />
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Danger Zone */}
                <div className="border-red-200 bg-red-50 p-4 rounded-lg">
                  <div className="flex items-start gap-3 mb-3">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-red-900">Danger Zone</p>
                      <p className="text-sm text-red-700">This action cannot be undone</p>
                    </div>
                  </div>
                  <Button variant="destructive" onClick={handleDeleteAccount}>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete My Account
                  </Button>
                </div>
              </CardContent>
            </Card>

          </TabsContent>
        )}

      </Tabs>
    </ModernPageWrapper>
  );
};

export default ModernSettingsPage;
