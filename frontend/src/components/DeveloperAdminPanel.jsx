import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Shield, Eye, EyeOff, Search, Copy, CheckCircle, Lock, Key, Database, RefreshCw, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Test credentials for role testing
const TEST_CREDENTIALS = [
  { role: 'developer', email: 'dev@test.com', password: 'Dev123!@#', description: 'Full system access' },
  { role: 'master', email: 'master@test.com', password: 'Master123!', description: 'Business owner access' },
  { role: 'admin', email: 'admin@test.com', password: 'Admin123!', description: 'Organization admin' },
  { role: 'operations_manager', email: 'opsmgr@test.com', password: 'Ops123!', description: 'Strategic operations' },
  { role: 'team_lead', email: 'teamlead@test.com', password: 'Lead123!', description: 'Team leadership' },
  { role: 'manager', email: 'manager@test.com', password: 'Mgr123!', description: 'Department management' },
  { role: 'supervisor', email: 'supervisor@test.com', password: 'Super123!', description: 'Shift supervision' },
  { role: 'inspector', email: 'inspector@test.com', password: 'Inspect123!', description: 'Execute operations' },
  { role: 'operator', email: 'operator@test.com', password: 'Oper123!', description: 'Basic tasks' },
  { role: 'viewer', email: 'viewer@test.com', password: 'View123!', description: 'Read-only access' },
];

const DeveloperAdminPanel = () => {
  const { user } = useAuth();
  const { isDeveloper } = usePermissions();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showPasswords, setShowPasswords] = useState({});
  const [showAllPasswords, setShowAllPasswords] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [resetPasswordDialog, setResetPasswordDialog] = useState(false);
  const [resetUser, setResetUser] = useState(null);
  const [newPassword, setNewPassword] = useState('Test123!');

  useEffect(() => {
    if (isDeveloper()) {
      loadData();
    }
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersRes, rolesRes, permsRes] = await Promise.all([
        axios.get(`${API}/users`),
        axios.get(`${API}/roles`),
        axios.get(`${API}/permissions`)
      ]);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
      setPermissions(permsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (userId) => {
    setShowPasswords(prev => ({
      ...prev,
      [userId]: !prev[userId]
    }));
  };

  const copyToClipboard = (text) => {
    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => {
          setCopiedId(text);
          setTimeout(() => setCopiedId(null), 2000);
        })
        .catch(() => {
          fallbackCopy(text);
        });
    } else {
      fallbackCopy(text);
    }
  };

  const fallbackCopy = (text) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
      document.execCommand('copy');
      setCopiedId(text);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      alert('Copy failed. Text: ' + text);
    }
    
    document.body.removeChild(textArea);
  };

  const handleResetPassword = async () => {
    if (!resetUser || !newPassword) return;
    
    try {
      await axios.put(`${API}/users/${resetUser.id}/password`, {
        new_password: newPassword
      });
      alert(`Password reset successfully for ${resetUser.name}!\nNew password: ${newPassword}`);
      setResetPasswordDialog(false);
      setResetUser(null);
      setNewPassword('Test123!');
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reset password');
    }
  };

  const getRoleBadgeStyle = (roleCode) => {
    const roleColors = {
      developer: '#6366f1',
      master: '#9333ea',
      admin: '#ef4444',
      operations_manager: '#f59e0b',
      team_lead: '#06b6d4',
      manager: '#3b82f6',
      supervisor: '#14b8a6',
      inspector: '#eab308',
      operator: '#64748b',
      viewer: '#bef264'
    };
    const color = roleColors[roleCode] || '#64748b';
    const textColor = roleCode === 'viewer' ? 'black' : 'white';
    return { backgroundColor: color, color: textColor };
  };

  const getPasswordStatus = (u) => {
    // Check both password and password_hash fields
    const passwordField = u.password || u.password_hash;
    
    if (!passwordField) {
      return { status: 'none', color: 'red', text: 'No Password' };
    }
    
    // Plain text passwords are typically < 50 chars
    // Hashed passwords (bcrypt) are typically 60 chars
    if (passwordField.length < 50) {
      return { status: 'known', color: 'green', text: 'Known Password' };
    } else {
      return { status: 'hashed', color: 'amber', text: 'Hashed (Unknown)' };
    }
  };

  const filteredUsers = users.filter(u =>
    u.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isDeveloper()) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Alert variant="destructive" className="max-w-md">
          <Lock className="h-4 w-4" />
          <AlertDescription>
            <strong>Access Denied:</strong> Developer role required to access this panel.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Shield className="h-8 w-8 text-purple-600" />
            Developer Admin Panel
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            System-wide access for testing and debugging • Role: Developer
          </p>
        </div>
        <Badge style={{ backgroundColor: '#6366f1', color: 'white' }} className="text-lg px-4 py-2">
          DEVELOPER ACCESS
        </Badge>
      </div>

      <Tabs defaultValue="test-creds" className="w-full">
        <TabsList>
          <TabsTrigger value="test-creds">
            <Key className="h-4 w-4 mr-2" />
            Test Credentials
          </TabsTrigger>
          <TabsTrigger value="users">
            <Database className="h-4 w-4 mr-2" />
            All Users
          </TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
        </TabsList>

        {/* Test Credentials Tab */}
        <TabsContent value="test-creds">
          <Card>
            <CardHeader>
              <CardTitle>Pre-configured Test Credentials</CardTitle>
              <CardDescription>
                Use these credentials to test each role's access • All passwords are known and visible
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Role</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Password</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {TEST_CREDENTIALS.map((cred) => (
                    <TableRow key={cred.role}>
                      <TableCell>
                        <Badge style={getRoleBadgeStyle(cred.role)}>
                          {cred.role}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{cred.email}</TableCell>
                      <TableCell>
                        <code className="bg-slate-100 px-2 py-1 rounded text-sm font-mono">
                          {cred.password}
                        </code>
                      </TableCell>
                      <TableCell className="text-sm text-slate-600">{cred.description}</TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(cred.password)}
                          title="Copy password only"
                        >
                          {copiedId === cred.password ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">Testing Instructions:</h4>
                <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
                  <li>Copy the password for the role you want to test</li>
                  <li>Open an <strong>incognito/private window</strong></li>
                  <li>Login with the email and password above</li>
                  <li>Verify menu items and features match role permissions</li>
                  <li>Test available CRUD operations</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* All Users Tab */}
        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>Database Users & Password Management</CardTitle>
              <CardDescription>
                All users in database • Total: {users.length} users • Password status indicators
              </CardDescription>
              <div className="flex gap-2 mt-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Button 
                  onClick={() => setShowAllPasswords(!showAllPasswords)} 
                  variant={showAllPasswords ? "default" : "outline"}
                >
                  {showAllPasswords ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                  {showAllPasswords ? 'Hide All' : 'Show All'}
                </Button>
                <Button onClick={loadData} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Password</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((u) => {
                      const pwStatus = getPasswordStatus(u);
                      return (
                        <TableRow key={u.id}>
                          <TableCell className="font-medium">{u.name}</TableCell>
                          <TableCell className="font-mono text-xs">{u.email}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <code className="bg-slate-100 px-2 py-1 rounded text-sm font-mono max-w-[150px] truncate">
                                {(showAllPasswords || showPasswords[u.id]) 
                                  ? (pwStatus.status === 'known' ? (u.password || u.password_hash) : (pwStatus.status === 'hashed' ? '••••••••(hashed)' : 'No password'))
                                  : '••••••••'}
                              </code>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => togglePasswordVisibility(u.id)}
                              >
                                {showPasswords[u.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                              </Button>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge 
                              variant="outline"
                              className={`text-xs ${
                                pwStatus.color === 'green' ? 'border-green-500 text-green-700' :
                                pwStatus.color === 'amber' ? 'border-amber-500 text-amber-700' :
                                'border-red-500 text-red-700'
                              }`}
                            >
                              {pwStatus.text}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge style={getRoleBadgeStyle(u.role)}>{u.role}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              {pwStatus.status === 'known' && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => copyToClipboard(u.password || u.password_hash)}
                                  title="Copy password only"
                                >
                                  {copiedId === (u.password || u.password_hash) ? (
                                    <CheckCircle className="h-4 w-4 text-green-600" />
                                  ) : (
                                    <Copy className="h-4 w-4" />
                                  )}
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  setResetUser(u);
                                  setResetPasswordDialog(true);
                                }}
                                title="Reset password for testing"
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>

              <div className="mt-4 flex gap-2 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span>Known Password (can view & copy)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-amber-500 rounded"></div>
                  <span>Hashed (use Reset button)</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span>No Password (use Reset button)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Roles Tab */}
        <TabsContent value="roles">
          <Card>
            <CardHeader>
              <CardTitle>All Roles</CardTitle>
              <CardDescription>System and custom roles • Total: {roles.length} roles</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Role</TableHead>
                    <TableHead>Code</TableHead>
                    <TableHead>Level</TableHead>
                    <TableHead>Color</TableHead>
                    <TableHead>Type</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {roles.sort((a, b) => a.level - b.level).map((role) => (
                    <TableRow key={role.id}>
                      <TableCell>
                        <Badge style={{ backgroundColor: role.color, color: role.code === 'viewer' ? 'black' : 'white' }}>
                          {role.name}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{role.code}</TableCell>
                      <TableCell>Level {role.level}</TableCell>
                      <TableCell>
                        <code className="text-xs bg-slate-100 px-2 py-1 rounded">{role.color}</code>
                      </TableCell>
                      <TableCell>
                        {role.is_system_role ? (
                          <Badge variant="outline">System</Badge>
                        ) : (
                          <Badge variant="secondary">Custom</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permissions Tab */}
        <TabsContent value="permissions">
          <Card>
            <CardHeader>
              <CardTitle>All Permissions</CardTitle>
              <CardDescription>System permissions • Total: {permissions.length} permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(
                  permissions.reduce((acc, perm) => {
                    if (!acc[perm.resource_type]) acc[perm.resource_type] = [];
                    acc[perm.resource_type].push(perm);
                    return acc;
                  }, {})
                ).map(([resource, perms]) => (
                  <div key={resource} className="border rounded-lg p-4">
                    <h3 className="font-semibold text-lg mb-2 capitalize">{resource}</h3>
                    <div className="grid grid-cols-2 gap-2">
                      {perms.map(perm => (
                        <div key={perm.id} className="text-sm">
                          <code className="bg-slate-100 px-2 py-1 rounded">
                            {perm.action}.{perm.scope}
                          </code>
                          <span className="ml-2 text-slate-600">{perm.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Reset Password Dialog */}
      <Dialog open={resetPasswordDialog} onOpenChange={setResetPasswordDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset Password for Testing</DialogTitle>
            <DialogDescription>
              Set a new password for {resetUser?.name} ({resetUser?.email})
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="text"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Test123!"
              />
              <p className="text-xs text-slate-500 mt-1">
                Recommended: Use a simple test password like "Test123!"
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setResetPasswordDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleResetPassword}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset Password
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DeveloperAdminPanel;
