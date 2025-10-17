// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Shield, Plus, Trash2, Lock, Save, Grid3x3, Eye, Edit, CheckCircle, Crown, Users } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import PermissionMatrixTable from './PermissionMatrixTable';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Role level to color mapping
const ROLE_COLORS = {
  1: { bg: 'bg-purple-500', text: 'text-purple-500', border: 'border-purple-500' },
  2: { bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500' },
  3: { bg: 'bg-purple-600', text: 'text-purple-600', border: 'border-purple-600' },
  4: { bg: 'bg-orange-500', text: 'text-orange-500', border: 'border-orange-500' },
  5: { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500' },
  6: { bg: 'bg-blue-600', text: 'text-blue-600', border: 'border-blue-600' },
  7: { bg: 'bg-green-600', text: 'text-green-600', border: 'border-green-600' },
  8: { bg: 'bg-yellow-500', text: 'text-yellow-500', border: 'border-yellow-500' },
  9: { bg: 'bg-gray-500', text: 'text-gray-500', border: 'border-gray-500' },
  10: { bg: 'bg-green-500', text: 'text-green-500', border: 'border-green-500' }
};

const RoleManagementPage = () => {
  const { toast } = useToast();
  const [roles, setRoles] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [rolePermissions, setRolePermissions] = useState<any>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [showPermissionsDialog, setShowPermissionsDialog] = useState<boolean>(false);
  const [selectedRole, setSelectedRole] = useState<any | null>(null);
  const [newRole, setNewRole] = useState({ 
    name: '', 
    code: '', 
    color: '#3b82f6', 
    level: 11, 
    description: '',
    selectedPermissions: []
  });

  useEffect(() => {
    loadRoles();
    loadPermissions();
  }, []);

  const loadRoles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/roles`);
      setRoles(response.data);
      
      // Load permissions for each role
      const permMap: { [key: string]: any } = {};
      for (const role of response.data) {
        try {
          const perms = await axios.get(`${API}/roles/${role.id}/permissions`);
          permMap[role.id] = perms.data.map((p: any) => p.permission_id);
        } catch (err: unknown) {
          permMap[role.id] = [];
        }
      }
      setRolePermissions(permMap);
    } catch (err: unknown) {
      console.error('Failed to load roles:', err);
      toast({
        title: 'Error',
        description: 'Failed to load roles',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPermissions = async () => {
    try {
      const response = await axios.get(`${API}/permissions`);
      setPermissions(response.data);
    } catch (err: unknown) {
      console.error('Failed to load permissions:', err);
    }
  };

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/roles`, {
        name: newRole.name,
        code: newRole.code,
        color: newRole.color,
        level: newRole.level,
        description: newRole.description
      });
      
      toast({
        title: 'Success',
        description: 'Custom role created successfully!',
      });
      
      setShowCreateDialog(false);
      setNewRole({ name: '', code: '', color: '#3b82f6', level: 11, description: '', selectedPermissions: [] });
      loadRoles();
    } catch (err: unknown) {
      toast({
        title: 'Error',
        description: (err as any).response?.data?.detail || 'Failed to create role',
        variant: 'destructive'
      });
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm('Are you sure you want to delete this role?')) return;
    
    try {
      await axios.delete(`${API}/roles/${roleId}`);
      toast({
        title: 'Success',
        description: 'Role deleted successfully',
      });
      loadRoles();
    } catch (err: unknown) {
      toast({
        title: 'Error',
        description: (err as any).response?.data?.detail || 'Failed to delete role',
        variant: 'destructive'
      });
    }
  };

  const handleViewPermissions = (role: any) => {
    setSelectedRole(role);
    setShowPermissionsDialog(true);
  };

  const systemRoles = roles.filter(r => r.is_system_role || r.is_system);
  const customRoles = roles.filter(r => !r.is_system_role && !r.is_system);

  const getRoleColor = (level: number) => {
    return ROLE_COLORS[level] || { bg: 'bg-gray-500', text: 'text-gray-500', border: 'border-gray-500' };
  };

  return (
    <ModernPageWrapper
      title="Role Management"
      subtitle="Configure roles and access control"
      actions={
        <Button onClick={() => setShowCreateDialog(true)} size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Role
        </Button>
      }
    >
      <div className="space-y-6">

      <Tabs defaultValue="system" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="system">System Roles</TabsTrigger>
          <TabsTrigger value="custom">Custom Roles</TabsTrigger>
          <TabsTrigger value="matrix">Permission Matrix</TabsTrigger>
        </TabsList>

        {/* System Roles Tab - Card Grid */}
        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Roles</CardTitle>
              <CardDescription>
                10 built-in roles with predefined permissions. System roles cannot be deleted.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-12 text-muted-foreground">Loading roles...</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                  {systemRoles.map((role) => {
                    const color = getRoleColor(role.level);
                    const permCount = rolePermissions[role.id]?.length || 0;
                    
                    return (
                      <Card key={role.id} className={`border-2 ${color.border} hover:shadow-lg transition-shadow`}>
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <Badge className={`${color.bg} text-white`}>
                              Level {role.level}
                            </Badge>
                            <Lock className="h-4 w-4 text-muted-foreground" />
                          </div>
                          <CardTitle className="text-lg mt-2">{role.name}</CardTitle>
                          <CardDescription className="text-xs">{role.code}</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="text-sm text-muted-foreground">
                            {role.description || 'System role with predefined permissions'}
                          </div>
                          <div className="flex items-center justify-between pt-2 border-t">
                            <span className="text-xs text-muted-foreground">Permissions</span>
                            <Badge variant="outline" className={color.text}>
                              {permCount} assigned
                            </Badge>
                          </div>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="w-full"
                            onClick={() => handleViewPermissions(role)}
                          >
                            <Eye className="h-3 w-3 mr-2" />
                            View Permissions
                          </Button>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Custom Roles Tab - Compact Table */}
        <TabsContent value="custom" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Custom Roles</CardTitle>
              <CardDescription>
                Create and manage custom roles tailored to your organization's needs.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {customRoles.length === 0 ? (
                <div className="text-center py-12">
                  <Grid3x3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Custom Roles</h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first custom role with specific permissions
                  </p>
                  <Button onClick={() => setShowCreateDialog(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Custom Role
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {customRoles.map((role) => {
                    const color = getRoleColor(role.level);
                    const permCount = rolePermissions[role.id]?.length || 0;
                    
                    return (
                      <Card key={role.id} className="border">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 flex-1">
                              <Badge className={`${color.bg} text-white`}>
                                Level {role.level}
                              </Badge>
                              <div className="flex-1">
                                <h4 className="font-semibold">{role.name}</h4>
                                <p className="text-sm text-muted-foreground">{role.code}</p>
                              </div>
                              <Badge variant="outline" className={color.text}>
                                {permCount} permissions
                              </Badge>
                            </div>
                            <div className="flex gap-2">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleViewPermissions(role)}
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleDeleteRole(role.id)}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permission Matrix Tab */}
        <TabsContent value="matrix" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Permission Matrix</CardTitle>
              <CardDescription>
                View and manage permissions for all roles in a single view
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <Grid3x3 className="h-12 w-12 mx-auto mb-4" />
                <p>Permission matrix view coming soon</p>
                <p className="text-sm mt-2">Use "View Permissions" on individual roles for now</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Custom Role Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create Custom Role</DialogTitle>
            <DialogDescription>
              Create a new custom role for your organization
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleCreateRole} className="space-y-4">
            <div>
              <Label htmlFor="name">Role Name</Label>
              <Input
                id="name"
                value={newRole.name}
                onChange={(e) => setNewRole({...newRole, name: e.target.value})}
                placeholder="e.g., Regional Manager"
                required
              />
            </div>

            <div>
              <Label htmlFor="code">Role Code</Label>
              <Input
                id="code"
                value={newRole.code}
                onChange={(e) => setNewRole({...newRole, code: e.target.value.toLowerCase().replace(/\s+/g, '_')})}
                placeholder="e.g., regional_manager"
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Lowercase with underscores (auto-formatted)
              </p>
            </div>

            <div>
              <Label htmlFor="level">Hierarchy Level</Label>
              <Input
                id="level"
                type="number"
                min="11"
                max="100"
                value={newRole.level}
                onChange={(e) => setNewRole({...newRole, level: parseInt(e.target.value)})}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                System roles use levels 1-10. Custom roles start at 11.
              </p>
            </div>

            <div>
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={newRole.description}
                onChange={(e) => setNewRole({...newRole, description: e.target.value})}
                placeholder="Brief description of this role..."
                rows={3}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">
                <Plus className="h-4 w-4 mr-2" />
                Create Role
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* View Permissions Dialog */}
      <Dialog open={showPermissionsDialog} onOpenChange={setShowPermissionsDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedRole?.name} - Permissions
            </DialogTitle>
            <DialogDescription>
              {selectedRole?.is_system ? 'System role permissions (read-only)' : 'Manage permissions for this role'}
            </DialogDescription>
          </DialogHeader>
          
          {selectedRole && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2 p-4 bg-muted rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">Role Code</p>
                  <p className="font-semibold">{selectedRole.code}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Level</p>
                  <p className="font-semibold">Level {selectedRole.level}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-sm text-muted-foreground">Permissions Assigned</p>
                  <p className="font-semibold">{rolePermissions[selectedRole.id]?.length || 0} / {permissions.length}</p>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Assigned Permissions</Label>
                <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto border rounded-lg p-4">
                  {permissions
                    .filter(p => rolePermissions[selectedRole.id]?.includes(p.id))
                    .map((perm) => (
                      <div key={perm.id} className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{perm.name}</p>
                          <p className="text-xs text-muted-foreground">{perm.resource}.{perm.action}.{perm.scope}</p>
                        </div>
                      </div>
                    ))}
                  
                  {rolePermissions[selectedRole.id]?.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No permissions assigned to this role
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPermissionsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      </div>
    </ModernPageWrapper>
  );
};

export default RoleManagementPage;
