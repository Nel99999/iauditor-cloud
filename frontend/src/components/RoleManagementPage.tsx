import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Shield, Plus, Trash2, Lock, Save, Grid3x3 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RoleManagementPage = () => {
  const [roles, setRoles] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [rolePermissions, setRolePermissions] = useState<any>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [newRole, setNewRole] = useState({ 
    name: '', 
    code: '', 
    color: '#3b82f6', 
    level: 11, 
    description: '',
    selectedPermissions: []
  });
  const [matrixChanges, setMatrixChanges] = useState<any>({});

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
      
      // If permissions selected, assign them
      if (newRole.selectedPermissions.length > 0) {
        const createdRoles = await axios.get(`${API}/roles`);
        const newRoleData = createdRoles.data.find((r: any) => r.code === newRole.code);
        if (newRoleData) {
          await axios.post(`${API}/roles/${newRoleData.id}/permissions/bulk`, newRole.selectedPermissions);
        }
      }
      
      alert('Role created successfully!');
      setShowCreateDialog(false);
      setNewRole({ name: '', code: '', color: '#3b82f6', level: 11, description: '', selectedPermissions: [] });
      loadRoles();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to create role');
    }
  };

  const handleDeleteRole = async (roleId: string, isSystemRole: boolean) => {
    if (isSystemRole) {
      alert('Cannot delete system roles');
      return;
    }
    if (window.confirm('Delete this role?')) {
      try {
        await axios.delete(`${API}/roles/${roleId}`);
        alert('Role deleted successfully!');
        loadRoles();
      } catch (err: unknown) {
        alert((err as any).response?.data?.detail || 'Failed to delete role');
      }
    }
  };

  const togglePermission = (roleId: string, permissionId: string) => {
    const key = `${roleId}-${permissionId}`;
    const currentPerms = rolePermissions[roleId] || [];
    const hasPermission = currentPerms.includes(permissionId);
    
    setMatrixChanges(prev => ({
      ...prev,
      [key]: !hasPermission
    }));
  };

  const saveRolePermissions = async (roleId: string) => {
    try {
      const currentPerms = rolePermissions[roleId] || [];
      const newPerms = [...currentPerms];
      
      // Apply changes
      Object.keys(matrixChanges).forEach((key: any) => {
        if (key.startsWith(`${roleId}-`)) {
          const permId = key.split('-')[1];
          const shouldHave = matrixChanges[key];
          
          if (shouldHave && !newPerms.includes(permId)) {
            newPerms.push(permId);
          } else if (!shouldHave && newPerms.includes(permId)) {
            const index = newPerms.indexOf(permId);
            newPerms.splice(index, 1);
          }
        }
      });
      
      await axios.post(`${API}/roles/${roleId}/permissions/bulk`, newPerms);
      alert('Permissions updated successfully!');
      
      // Clear changes for this role
      const clearedChanges = {};
      Object.keys(matrixChanges).forEach((key: any) => {
        if (!key.startsWith(`${roleId}-`)) {
          clearedChanges[key] = matrixChanges[key];
        }
      });
      setMatrixChanges(clearedChanges);
      
      // Reload
      loadRoles();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to update permissions');
    }
  };

  const isPermissionChecked = (roleId: string, permissionId: string) => {
    const key = `${roleId}-${permissionId}`;
    if (key in matrixChanges) {
      return matrixChanges[key];
    }
    return (rolePermissions[roleId] || []).includes(permissionId);
  };

  const hasChanges = (roleId: any) => {
    return Object.keys(matrixChanges).some((key: any) => key.startsWith(`${roleId}-`));
  };

  // const _groupPermissionsByResource = () => {
  //   const grouped = {};
  //   permissions.forEach((perm: any) => {
  //     if (!grouped[perm.resource_type]) {
  //       grouped[perm.resource_type] = [];
  //     }
  //     grouped[perm.resource_type].push(perm);
  //   });
  //   return grouped;
  // };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Role Management</h1>
          <p className="text-slate-600 dark:text-slate-400">Manage roles and permissions</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Role
        </Button>
      </div>

      <Tabs defaultValue="roles" className="w-full">
        <TabsList>
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="permissions">
            <Grid3x3 className="h-4 w-4 mr-2" />
            Permission Matrix
          </TabsTrigger>
        </TabsList>

        {/* Roles Tab */}
        <TabsContent value="roles">
          <Card>
            <CardHeader>
              <CardTitle>System & Custom Roles</CardTitle>
              <CardDescription>10 system roles + custom roles for your organization</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading...</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Role</TableHead>
                      <TableHead>Code</TableHead>
                      <TableHead>Level</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {roles.map((role) => (
                      <TableRow key={role.id}>
                        <TableCell>
                          <Badge style={{ backgroundColor: role.color, color: 'white' }}>
                            {role.name}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{role.code}</TableCell>
                        <TableCell>{role.level}</TableCell>
                        <TableCell className="max-w-md truncate">{role.description}</TableCell>
                        <TableCell>
                          {role.is_system_role ? (
                            <Badge variant="outline">
                              <Lock className="h-3 w-3 mr-1" />
                              System
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Custom</Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          {!role.is_system_role && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDeleteRole(role.id, role.is_system_role)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Permission Matrix Tab */}
        <TabsContent value="permissions">
          <Card>
            <CardHeader>
              <CardTitle>Permission Matrix</CardTitle>
              <CardDescription>
                System roles (locked) are pre-configured. Custom roles can be modified. Check/uncheck boxes and click Save.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border">
                  <thead>
                    <tr className="bg-slate-100 border-b">
                      <th className="text-left p-3 font-semibold sticky left-0 bg-slate-100">Permission</th>
                      {roles.sort((a: any, b: any) => a.level - b.level).map((role: any) => (
                        <th key={role.id} className="p-2 text-center min-w-[100px]">
                          <div className="flex flex-col items-center gap-1">
                            <Badge 
                              style={{ backgroundColor: role.color, color: 'white' }}
                              className="text-xs"
                            >
                              {role.name}
                            </Badge>
                            {role.is_system_role && (
                              <Lock className="h-3 w-3 text-slate-400" />
                            )}
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {permissions.map((perm: any) => (
                      <tr key={perm.id} className="border-b hover:bg-slate-50">
                        <td className="p-3 sticky left-0 bg-white">
                          <div>
                            <span className="font-medium">{perm.resource_type}.{perm.action}.{perm.scope}</span>
                            <p className="text-xs text-slate-500">{perm.description}</p>
                          </div>
                        </td>
                        {roles.sort((a: any, b: any) => a.level - b.level).map((role: any) => (
                          <td key={role.id} className="p-2 text-center">
                            <Checkbox
                              checked={isPermissionChecked(role.id, perm.id)}
                              onCheckedChange={() => !role.is_system_role && togglePermission(role.id, perm.id)}
                              disabled={role.is_system_role}
                              className={role.is_system_role ? 'opacity-50 cursor-not-allowed' : ''}
                            />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Save buttons for custom roles only */}
              <div className="flex gap-2 flex-wrap mt-4">
                {roles.filter((r: any) => !r.is_system_role).map((role: any) => (
                  hasChanges(role.id) && (
                    <Button
                      key={role.id}
                      onClick={() => saveRolePermissions(role.id)}
                      style={{ backgroundColor: role.color, color: 'white' }}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save {role.name}
                    </Button>
                  )
                ))}
              </div>

              {roles.filter((r: any) => !r.is_system_role).length === 0 && (
                <p className="text-center text-slate-500 mt-4">
                  No custom roles to modify. System roles are locked and pre-configured.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Role Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Custom Role</DialogTitle>
            <DialogDescription>Define a new role with specific permissions</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateRole} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Role Name</Label>
                <Input
                  id="name"
                  value={newRole.name}
                  onChange={(e: any) => setNewRole({ ...newRole, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="code">Role Code</Label>
                <Input
                  id="code"
                  value={newRole.code}
                  onChange={(e: any) => setNewRole({ ...newRole, code: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                  placeholder="e.g., custom_role"
                  required
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="color">Badge Color</Label>
                <Input
                  id="color"
                  type="color"
                  value={newRole.color}
                  onChange={(e: any) => setNewRole({ ...newRole, color: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="level">Hierarchy Level (11+)</Label>
                <Input
                  id="level"
                  type="number"
                  min="11"
                  value={newRole.level}
                  onChange={(e: any) => setNewRole({ ...newRole, level: parseInt(e.target.value) })}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={newRole.description}
                onChange={(e: any) => setNewRole({ ...newRole, description: e.target.value })}
                required
              />
            </div>

            <div>
              <Label>Select Permissions (Optional)</Label>
              <div className="border rounded-lg p-4 max-h-64 overflow-y-auto space-y-2">
                {permissions.map((perm: any) => (
                  <div key={perm.id} className="flex items-center space-x-2">
                    <Checkbox
                      checked={newRole.selectedPermissions as any.includes(perm.id)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setNewRole({
                            ...newRole,
                            selectedPermissions as any: [...newRole.selectedPermissions, perm.id]
                          });
                        } else {
                          setNewRole({
                            ...newRole,
                            selectedPermissions: newRole.selectedPermissions.filter((p: any) => p !== perm.id)
                          });
                        }
                      }}
                    />
                    <label className="text-sm">
                      <span className="font-medium">{perm.resource_type}.{perm.action}.{perm.scope}</span>
                      <span className="text-slate-500 ml-2">{perm.description}</span>
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Selected: {newRole.selectedPermissions.length} permissions
              </p>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Create Role</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RoleManagementPage;
