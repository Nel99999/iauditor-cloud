import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import {
  Shield, Eye, EyeOff, Search, Copy, CheckCircle, Lock, Key, Database, RefreshCw,
  Activity, Cpu, HardDrive, Server, Mail, Code, Terminal, Zap, BarChart3,
  Webhook, Users as UsersIcon, Clock, Download, Play, AlertCircle, CheckCircle2, X
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

const DeveloperAdminPanelFull = () => {
  const { isDeveloper } = usePermissions();

  // Existing state
  const [users, setUsers] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showPasswords, setShowPasswords] = useState<any>({});
  const [showAllPasswords, setShowAllPasswords] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<any | null>(null);
  const [resetPasswordDialog, setResetPasswordDialog] = useState<boolean>(false);
  const [resetUser, setResetUser] = useState<any | null>(null);
  const [newPassword, setNewPassword] = useState('Test123!');

  // New state for DevOps features
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [environmentInfo, setEnvironmentInfo] = useState<any>(null);
  const [apiTestMethod, setApiTestMethod] = useState('GET');
  const [apiTestEndpoint, setApiTestEndpoint] = useState('/api/users');
  const [apiTestBody, setApiTestBody] = useState('{}');
  const [apiTestResult, setApiTestResult] = useState<any>(null);
  const [emailTestRecipient, setEmailTestRecipient] = useState('');
  const [emailTestTemplate, setEmailTestTemplate] = useState('welcome');
  const [emailTestResult, setEmailTestResult] = useState<any>(null);
  const [backendLogs, setBackendLogs] = useState<any[]>([]);
  const [frontendLogs, setFrontendLogs] = useState<any[]>([]);
  const [dbCollections, setDbCollections] = useState<any[]>([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [dbQuery, setDbQuery] = useState('{}');
  const [dbOperation, setDbOperation] = useState('find');
  const [dbResult, setDbResult] = useState<any>(null);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [activeSessions, setActiveSessions] = useState<any[]>([]);

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
    } catch (err: unknown) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  // System Health
  const loadSystemHealth = async () => {
    try {
      const res = await axios.get(`${API}/developer/health`);
      setSystemHealth(res.data);
    } catch (err) {
      console.error('Failed to load system health:', err);
    }
  };

  // Environment Info
  const loadEnvironmentInfo = async () => {
    try {
      const res = await axios.get(`${API}/developer/environment`);
      setEnvironmentInfo(res.data);
    } catch (err) {
      console.error('Failed to load environment info:', err);
    }
  };

  // API Testing
  const testApiEndpoint = async () => {
    try {
      const res = await axios.post(`${API}/developer/test/api`, {
        method: apiTestMethod,
        endpoint: apiTestEndpoint,
        headers: {},
        body: apiTestMethod !== 'GET' ? JSON.parse(apiTestBody) : {}
      });
      setApiTestResult(res.data);
    } catch (err) {
      setApiTestResult({ error: err.message });
    }
  };

  // Email Testing
  const testEmail = async () => {
    try {
      const res = await axios.post(`${API}/developer/test/email`, {
        recipient: emailTestRecipient,
        template_type: emailTestTemplate,
        test_data: {
          name: 'Test User',
          login_url: 'https://app.example.com/login',
          reset_url: 'https://app.example.com/reset?token=test123',
          inviter_name: 'Test Admin',
          organization_name: 'Test Organization',
          invite_url: 'https://app.example.com/accept?token=test123'
        }
      });
      setEmailTestResult(res.data);
    } catch (err) {
      setEmailTestResult({ error: err.message });
    }
  };

  // Logs
  const loadBackendLogs = async () => {
    try {
      const res = await axios.get(`${API}/developer/logs/backend?lines=100`);
      setBackendLogs(res.data.logs || []);
    } catch (err) {
      console.error('Failed to load backend logs:', err);
    }
  };

  const loadFrontendLogs = async () => {
    try {
      const res = await axios.get(`${API}/developer/logs/frontend?lines=100`);
      setFrontendLogs(res.data.logs || []);
    } catch (err) {
      console.error('Failed to load frontend logs:', err);
    }
  };

  // Database
  const loadCollections = async () => {
    try {
      const res = await axios.get(`${API}/developer/database/collections`);
      setDbCollections(res.data.collections || []);
    } catch (err) {
      console.error('Failed to load collections:', err);
    }
  };

  const executeDbQuery = async () => {
    try {
      const res = await axios.post(`${API}/developer/database/query`, {
        collection: selectedCollection,
        operation: dbOperation,
        query: JSON.parse(dbQuery),
        limit: 50
      });
      setDbResult(res.data);
    } catch (err) {
      setDbResult({ error: err.message });
    }
  };

  // Webhooks
  const loadWebhooks = async () => {
    try {
      const res = await axios.get(`${API}/developer/webhooks`);
      setWebhooks(res.data.webhooks || []);
    } catch (err) {
      console.error('Failed to load webhooks:', err);
    }
  };

  // Performance
  const loadPerformanceMetrics = async () => {
    try {
      const res = await axios.get(`${API}/developer/metrics/performance`);
      setPerformanceMetrics(res.data);
    } catch (err) {
      console.error('Failed to load performance metrics:', err);
    }
  };

  // Sessions
  const loadActiveSessions = async () => {
    try {
      const res = await axios.get(`${API}/developer/sessions/active`);
      setActiveSessions(res.data.sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await axios.delete(`${API}/developer/sessions/${sessionId}`);
      loadActiveSessions();
      alert('Session deleted successfully');
    } catch (err) {
      alert('Failed to delete session: ' + err.message);
    }
  };

  // Quick Actions
  const clearCache = async () => {
    try {
      await axios.post(`${API}/developer/actions/clear-cache`);
      alert('Cache cleared successfully');
    } catch (err) {
      alert('Failed to clear cache: ' + err.message);
    }
  };

  const impersonateUser = async (userId: string) => {
    try {
      const res = await axios.post(`${API}/developer/actions/impersonate`, { user_id: userId });
      alert(`Impersonation token generated!\n\nToken: ${res.data.token}\n\nExpires in: ${res.data.expires_in_minutes} minutes`);
    } catch (err) {
      alert('Failed to impersonate user: ' + err.message);
    }
  };

  // Utility functions
  const togglePasswordVisibility = (userId: any) => {
    setShowPasswords(prev => ({
      ...prev,
      [userId]: !prev[userId]
    }));
  };

  const copyToClipboard = (text: any) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => {
          setCopiedId(text);
          setTimeout(() => setCopiedId(null), 2000);
        })
        .catch(() => fallbackCopy(text));
    } else {
      fallbackCopy(text);
    }
  };

  const fallbackCopy = (text: any) => {
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
    } catch (err: unknown) {
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
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to reset password');
    }
  };

  const getRoleBadgeStyle = (roleCode: any) => {
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

  const getPasswordStatus = (u: any) => {
    const passwordField = u.password || u.password_hash;

    if (!passwordField) {
      return { status: 'none', color: 'red', text: 'No Password' };
    }

    if (passwordField.length < 50) {
      return { status: 'known', color: 'green', text: 'Known Password' };
    } else {
      return { status: 'hashed', color: 'amber', text: 'Hashed (Unknown)' };
    }
  };

  const filteredUsers = users.filter((u: any) =>
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
            Full DevOps Dashboard • System-wide access for testing and debugging
          </p>
        </div>
        <Badge style={{ backgroundColor: '#6366f1', color: 'white' }} className="text-lg px-4 py-2">
          DEVELOPER ACCESS
        </Badge>
      </div>

      <Tabs defaultValue="test-creds" className="w-full">
        <TabsList className="grid grid-cols-5 lg:grid-cols-10 gap-1">
          <TabsTrigger value="test-creds" className="text-xs">
            <Key className="h-3 w-3 mr-1" />
            Test Creds
          </TabsTrigger>
          <TabsTrigger value="users" className="text-xs">
            <Database className="h-3 w-3 mr-1" />
            Users
          </TabsTrigger>
          <TabsTrigger value="roles" className="text-xs">Roles</TabsTrigger>
          <TabsTrigger value="permissions" className="text-xs">Perms</TabsTrigger>
          <TabsTrigger value="health" className="text-xs">
            <Activity className="h-3 w-3 mr-1" />
            Health
          </TabsTrigger>
          <TabsTrigger value="api-test" className="text-xs">
            <Code className="h-3 w-3 mr-1" />
            API Test
          </TabsTrigger>
          <TabsTrigger value="email-test" className="text-xs">
            <Mail className="h-3 w-3 mr-1" />
            Email
          </TabsTrigger>
          <TabsTrigger value="logs" className="text-xs">
            <Terminal className="h-3 w-3 mr-1" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="database" className="text-xs">
            <Database className="h-3 w-3 mr-1" />
            DB
          </TabsTrigger>
          <TabsTrigger value="advanced" className="text-xs">
            <Zap className="h-3 w-3 mr-1" />
            Advanced
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Test Credentials */}
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

        {/* Tab 2: All Users (existing) */}
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
                              className={`text-xs ${pwStatus.color === 'green' ? 'border-green-500 text-green-700' :
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

        {/* Tab 3: Roles (existing) */}
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
                  {roles.sort((a: any, b: any) => a.level - b.level).map((role) => (
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

        {/* Tab 4: Permissions (existing) */}
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
                      {perms.map((perm: any) => (
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

        {/* Tab 5: System Health */}
        <TabsContent value="health">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      System Health Dashboard
                    </CardTitle>
                    <CardDescription>Real-time system metrics and status</CardDescription>
                  </div>
                  <Button onClick={loadSystemHealth}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {systemHealth ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* CPU */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Cpu className="h-4 w-4" />
                          CPU Usage
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">{systemHealth.system?.cpu_percent?.toFixed(1)}%</div>
                      </CardContent>
                    </Card>

                    {/* Memory */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Server className="h-4 w-4" />
                          Memory
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">{systemHealth.system?.memory?.percent?.toFixed(1)}%</div>
                        <div className="text-xs text-slate-500">
                          {(systemHealth.system?.memory?.used_mb / 1024).toFixed(2)} GB / {(systemHealth.system?.memory?.total_mb / 1024).toFixed(2)} GB
                        </div>
                      </CardContent>
                    </Card>

                    {/* Disk */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <HardDrive className="h-4 w-4" />
                          Disk Space
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-3xl font-bold">{systemHealth.system?.disk?.percent?.toFixed(1)}%</div>
                        <div className="text-xs text-slate-500">
                          {systemHealth.system?.disk?.used_gb?.toFixed(2)} GB / {systemHealth.system?.disk?.total_gb?.toFixed(2)} GB
                        </div>
                      </CardContent>
                    </Card>

                    {/* Database */}
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <Database className="h-4 w-4" />
                          MongoDB
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <Badge variant={systemHealth.database?.status === 'connected' ? 'default' : 'destructive'}>
                          {systemHealth.database?.status}
                        </Badge>
                        <div className="text-sm mt-2">
                          <div>Collections: {systemHealth.database?.collections}</div>
                          <div>Size: {systemHealth.database?.size_mb?.toFixed(2)} MB</div>
                          <div className="text-xs text-slate-500 mt-1">
                            Users: {systemHealth.database?.counts?.users} |
                            Roles: {systemHealth.database?.counts?.roles} |
                            Orgs: {systemHealth.database?.counts?.organizations}
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Services */}
                    <Card className="md:col-span-2">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Services Status</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex gap-4">
                          <div>
                            <Badge variant="default" className="bg-green-500">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Backend: {systemHealth.services?.backend}
                            </Badge>
                          </div>
                          <div>
                            <Badge variant="secondary">
                              Frontend: {systemHealth.services?.frontend}
                            </Badge>
                          </div>
                        </div>
                        <div className="text-xs text-slate-500 mt-2">
                          Last updated: {new Date(systemHealth.timestamp).toLocaleString()}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Button onClick={loadSystemHealth}>
                      Load System Health
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Environment Info */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Environment Configuration</CardTitle>
                    <CardDescription>System environment and configuration details</CardDescription>
                  </div>
                  <Button onClick={loadEnvironmentInfo} variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Load
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {environmentInfo && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Environment Variables</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {Object.entries(environmentInfo.environment_variables || {}).map(([key, value]: [string, any]) => (
                          <div key={key} className="flex justify-between border-b pb-1">
                            <span className="font-mono text-xs">{key}</span>
                            <span className="font-mono text-xs text-slate-600">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Separator />

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold mb-2">System Info</h4>
                        <div className="text-sm space-y-1">
                          <div>Environment: <Badge>{environmentInfo.environment}</Badge></div>
                          <div>Python: {environmentInfo.python_version}</div>
                          <div className="text-xs text-slate-500">Path: {environmentInfo.backend_path}</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold mb-2">Git Info</h4>
                        <div className="text-sm space-y-1">
                          {environmentInfo.git?.branch ? (
                            <>
                              <div>Branch: <code className="bg-slate-100 px-2 py-1 rounded">{environmentInfo.git.branch}</code></div>
                              <div>Commit: <code className="bg-slate-100 px-2 py-1 rounded">{environmentInfo.git.commit}</code></div>
                            </>
                          ) : (
                            <div className="text-slate-500">Git info not available</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab 6: API Tester */}
        <TabsContent value="api-test">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                API Endpoint Tester
              </CardTitle>
              <CardDescription>Test any API endpoint with custom method, headers, and body</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-4 gap-4">
                <div className="col-span-1">
                  <Label>Method</Label>
                  <Select value={apiTestMethod} onValueChange={setApiTestMethod}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="DELETE">DELETE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="col-span-3">
                  <Label>Endpoint</Label>
                  <Input
                    value={apiTestEndpoint}
                    onChange={(e) => setApiTestEndpoint(e.target.value)}
                    placeholder="/api/users"
                  />
                </div>
              </div>

              {apiTestMethod !== 'GET' && (
                <div>
                  <Label>Request Body (JSON)</Label>
                  <Textarea
                    value={apiTestBody}
                    onChange={(e) => setApiTestBody(e.target.value)}
                    placeholder='{"key": "value"}'
                    rows={6}
                    className="font-mono text-sm"
                  />
                </div>
              )}

              <Button onClick={testApiEndpoint} className="w-full">
                <Play className="h-4 w-4 mr-2" />
                Execute Request
              </Button>

              {apiTestResult && (
                <div className="mt-4">
                  <Label>Response</Label>
                  <div className="border rounded-lg p-4 bg-slate-50">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={apiTestResult.status_code < 400 ? 'default' : 'destructive'}>
                        Status: {apiTestResult.status_code || 'Error'}
                      </Badge>
                      {apiTestResult.elapsed_ms && (
                        <Badge variant="outline">{apiTestResult.elapsed_ms.toFixed(2)} ms</Badge>
                      )}
                    </div>
                    <ScrollArea className="h-64">
                      <pre className="text-xs font-mono whitespace-pre-wrap">
                        {JSON.stringify(apiTestResult.json || apiTestResult.body || apiTestResult, null, 2)}
                      </pre>
                    </ScrollArea>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 7: Email Tester */}
        <TabsContent value="email-test">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Email Testing Tool
              </CardTitle>
              <CardDescription>Send test emails via SendGrid</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Recipient Email</Label>
                <Input
                  value={emailTestRecipient}
                  onChange={(e) => setEmailTestRecipient(e.target.value)}
                  placeholder="test@example.com"
                  type="email"
                />
              </div>

              <div>
                <Label>Template Type</Label>
                <Select value={emailTestTemplate} onValueChange={setEmailTestTemplate}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="welcome">Welcome Email</SelectItem>
                    <SelectItem value="password_reset">Password Reset</SelectItem>
                    <SelectItem value="invitation">Invitation</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={testEmail} className="w-full">
                <Mail className="h-4 w-4 mr-2" />
                Send Test Email
              </Button>

              {emailTestResult && (
                <Alert variant={emailTestResult.success ? 'default' : 'destructive'}>
                  <AlertDescription>
                    {emailTestResult.success ? (
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        Email sent successfully to {emailTestResult.recipient}
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        Error: {emailTestResult.error}
                      </div>
                    )}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 8: Logs Viewer */}
        <TabsContent value="logs">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Terminal className="h-5 w-5" />
                      Backend Logs
                    </CardTitle>
                    <CardDescription>Last 100 lines from backend service</CardDescription>
                  </div>
                  <Button onClick={loadBackendLogs}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64 border rounded-lg p-4 bg-slate-50">
                  <div className="font-mono text-xs space-y-1">
                    {backendLogs.length > 0 ? (
                      backendLogs.map((log, idx) => (
                        <div key={idx} className={log.type === 'error' ? 'text-red-600' : 'text-slate-700'}>
                          {log.message}
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500">Click "Refresh" to load logs</div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Terminal className="h-5 w-5" />
                      Frontend Logs
                    </CardTitle>
                    <CardDescription>Last 100 lines from frontend service</CardDescription>
                  </div>
                  <Button onClick={loadFrontendLogs}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64 border rounded-lg p-4 bg-slate-50">
                  <div className="font-mono text-xs space-y-1">
                    {frontendLogs.length > 0 ? (
                      frontendLogs.map((log, idx) => (
                        <div key={idx} className={log.type === 'error' ? 'text-red-600' : 'text-slate-700'}>
                          {log.message}
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-500">Click "Refresh" to load logs</div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab 9: Database Query Interface */}
        <TabsContent value="database">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Database Query Interface
                  </CardTitle>
                  <CardDescription>Execute queries on MongoDB collections (use with caution)</CardDescription>
                </div>
                <Button onClick={loadCollections} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Load Collections
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Collection</Label>
                  <Select value={selectedCollection} onValueChange={setSelectedCollection}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select collection" />
                    </SelectTrigger>
                    <SelectContent>
                      {dbCollections.map((coll) => (
                        <SelectItem key={coll.name} value={coll.name}>
                          {coll.name} ({coll.count} docs)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Operation</Label>
                  <Select value={dbOperation} onValueChange={setDbOperation}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="find">Find</SelectItem>
                      <SelectItem value="count">Count</SelectItem>
                      <SelectItem value="update">Update (requires confirm)</SelectItem>
                      <SelectItem value="delete">Delete (requires confirm)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label>Query (JSON)</Label>
                <Textarea
                  value={dbQuery}
                  onChange={(e) => setDbQuery(e.target.value)}
                  placeholder='{"field": "value"}'
                  rows={6}
                  className="font-mono text-sm"
                />
              </div>

              <Button onClick={executeDbQuery} className="w-full" variant={dbOperation.match(/update|delete/) ? 'destructive' : 'default'}>
                <Play className="h-4 w-4 mr-2" />
                Execute Query
              </Button>

              {dbResult && (
                <div className="mt-4">
                  <Label>Result</Label>
                  <div className="border rounded-lg p-4 bg-slate-50">
                    <div className="mb-2">
                      <Badge>{dbResult.operation}</Badge>
                      {dbResult.count !== undefined && (
                        <Badge variant="outline" className="ml-2">
                          {dbResult.count} results
                        </Badge>
                      )}
                    </div>
                    <ScrollArea className="h-64">
                      <pre className="text-xs font-mono whitespace-pre-wrap">
                        {JSON.stringify(dbResult, null, 2)}
                      </pre>
                    </ScrollArea>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 10: Advanced Features */}
        <TabsContent value="advanced">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sessions */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Active Sessions
                    </CardTitle>
                  </div>
                  <Button onClick={loadActiveSessions} size="sm" variant="outline">
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Load
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold mb-2">{activeSessions.length}</div>
                <ScrollArea className="h-32">
                  {activeSessions.length > 0 ? (
                    <div className="space-y-2">
                      {activeSessions.map((session) => (
                        <div key={session.id} className="flex justify-between items-center text-sm border-b pb-1">
                          <span className="text-xs font-mono">{session.user_id?.substring(0, 8)}...</span>
                          <Button size="sm" variant="ghost" onClick={() => deleteSession(session.id)}>
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500">No sessions or click Load</div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button onClick={clearCache} variant="outline" className="w-full justify-start" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Clear Cache
                </Button>
                <Button onClick={() => {
                  const userId = prompt('Enter User ID to impersonate:');
                  if (userId) impersonateUser(userId);
                }} variant="outline" className="w-full justify-start" size="sm">
                  <UsersIcon className="h-4 w-4 mr-2" />
                  Impersonate User
                </Button>
              </CardContent>
            </Card>

            {/* Webhooks */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Webhook className="h-4 w-4" />
                      Webhooks
                    </CardTitle>
                  </div>
                  <Button onClick={loadWebhooks} size="sm" variant="outline">
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Load
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold mb-2">{webhooks.length}</div>
                <div className="text-sm text-slate-500">
                  {webhooks.length > 0 ? `${webhooks.length} webhooks configured` : 'No webhooks or click Load'}
                </div>
              </CardContent>
            </Card>

            {/* Performance */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-sm flex items-center gap-2">
                      <BarChart3 className="h-4 w-4" />
                      Performance
                    </CardTitle>
                  </div>
                  <Button onClick={loadPerformanceMetrics} size="sm" variant="outline">
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Load
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {performanceMetrics ? (
                  <div>
                    <div className="text-2xl font-bold mb-2">{performanceMetrics.total_requests}</div>
                    <div className="text-sm text-slate-500">Total requests analyzed</div>
                  </div>
                ) : (
                  <div className="text-sm text-slate-500">Click Load for metrics</div>
                )}
              </CardContent>
            </Card>
          </div>
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

export default DeveloperAdminPanelFull;
