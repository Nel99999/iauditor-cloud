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
import { Shield, Eye, EyeOff, Search, Copy, CheckCircle, Lock, Key, Database } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DeveloperAdminPanel = () => {
  const { user } = useAuth();
  const { isDeveloper } = usePermissions();
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showPasswords, setShowPasswords] = useState({});
  const [copiedId, setCopiedId] = useState(null);

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

  const copyToClipboard = (text, userId) => {
    navigator.clipboard.writeText(text);
    setCopiedId(userId);
    setTimeout(() => setCopiedId(null), 2000);
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
      viewer: '#22c55e'
    };
    const color = roleColors[roleCode] || '#64748b';
    return { backgroundColor: color, color: 'white' };
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

      <Tabs defaultValue="users" className="w-full">
        <TabsList>
          <TabsTrigger value="users">
            <Key className="h-4 w-4 mr-2" />
            Users & Passwords
          </TabsTrigger>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="database">Database Info</TabsTrigger>
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>All Users & Test Credentials</CardTitle>
              <CardDescription>
                View all user credentials for testing role-based access • Total: {users.length} users
              </CardDescription>
              <div className="flex gap-2 mt-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search users by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Button onClick={loadData} variant="outline">
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading...</p>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Password</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredUsers.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell className="font-medium">{u.name}</TableCell>
                          <TableCell>{u.email}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <code className="bg-slate-100 px-2 py-1 rounded text-sm">
                                {showPasswords[u.id] ? (u.password || '••••••••') : '••••••••'}
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
                            <Badge style={getRoleBadgeStyle(u.role)}>
                              {u.role}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {u.deleted ? (
                              <Badge variant="destructive">Deleted</Badge>
                            ) : (
                              <Badge variant="success" className="bg-green-100 text-green-800">Active</Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => copyToClipboard(`Email: ${u.email}\nPassword: ${u.password || 'N/A'}`, u.id)}
                            >
                              {copiedId === u.id ? (
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
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Login Instructions */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Testing Instructions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p><strong>To test different roles:</strong></p>
                <ol className="list-decimal list-inside space-y-1 ml-2">
                  <li>Copy email and password from the table above</li>
                  <li>Open an incognito/private window</li>
                  <li>Login with the copied credentials</li>
                  <li>Verify that menu items and features match the role's permissions</li>
                  <li>Test CRUD operations available to that role</li>
                </ol>
                <p className="mt-4 text-amber-600">
                  <strong>Note:</strong> Passwords shown here are test credentials. In production, passwords are hashed and cannot be viewed.
                </p>
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
                    <TableHead>Type</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {roles.sort((a, b) => a.level - b.level).map((role) => (
                    <TableRow key={role.id}>
                      <TableCell>
                        <Badge style={{ backgroundColor: role.color, color: 'white' }}>
                          {role.name}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{role.code}</TableCell>
                      <TableCell>Level {role.level}</TableCell>
                      <TableCell>
                        {role.is_system_role ? (
                          <Badge variant="outline">System</Badge>
                        ) : (
                          <Badge variant="secondary">Custom</Badge>
                        )}
                      </TableCell>
                      <TableCell className="max-w-md">{role.description}</TableCell>
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

        {/* Database Info Tab */}
        <TabsContent value="database">
          <Card>
            <CardHeader>
              <CardTitle>Database Statistics</CardTitle>
              <CardDescription>Current system data overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="border rounded-lg p-4">
                  <Database className="h-8 w-8 text-blue-600 mb-2" />
                  <p className="text-2xl font-bold">{users.length}</p>
                  <p className="text-sm text-slate-600">Total Users</p>
                </div>
                <div className="border rounded-lg p-4">
                  <Shield className="h-8 w-8 text-purple-600 mb-2" />
                  <p className="text-2xl font-bold">{roles.length}</p>
                  <p className="text-sm text-slate-600">Total Roles</p>
                </div>
                <div className="border rounded-lg p-4">
                  <Key className="h-8 w-8 text-green-600 mb-2" />
                  <p className="text-2xl font-bold">{permissions.length}</p>
                  <p className="text-sm text-slate-600">Total Permissions</p>
                </div>
              </div>
              
              <div className="mt-6 space-y-2">
                <h4 className="font-semibold">User Distribution by Role:</h4>
                {roles.filter(r => r.is_system_role).sort((a, b) => a.level - b.level).map(role => {
                  const count = users.filter(u => u.role === role.code).length;
                  return (
                    <div key={role.id} className="flex items-center justify-between p-2 border-b">
                      <Badge style={{ backgroundColor: role.color, color: 'white' }}>
                        {role.name}
                      </Badge>
                      <span className="font-semibold">{count} users</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DeveloperAdminPanel;
