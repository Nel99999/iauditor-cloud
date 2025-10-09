import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Shield, Plus, Edit, Trash2, Lock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RoleManagementPage = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newRole, setNewRole] = useState({ name: '', code: '', color: '#3b82f6', level: 11, description: '' });

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/roles`);
      setRoles(response.data);
    } catch (err) {
      console.error('Failed to load roles:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRole = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/roles`, newRole);
      alert('Role created successfully!');
      setShowCreateDialog(false);
      setNewRole({ name: '', code: '', color: '#3b82f6', level: 11, description: '' });
      loadRoles();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create role');
    }
  };

  const handleDeleteRole = async (roleId, isSystemRole) => {
    if (isSystemRole) {
      alert('Cannot delete system roles');
      return;
    }
    if (window.confirm('Delete this role?')) {
      try {
        await axios.delete(`${API}/roles/${roleId}`);
        alert('Role deleted successfully!');
        loadRoles();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete role');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Role Management</h1>
          <p className="text-slate-600 dark:text-slate-400">Manage user roles and permissions</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Role
        </Button>
      </div>

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

      {/* Create Role Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Custom Role</DialogTitle>
            <DialogDescription>Define a new role for your organization</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateRole} className="space-y-4">
            <div>
              <Label htmlFor="name">Role Name</Label>
              <Input
                id="name"
                value={newRole.name}
                onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
                required
              />
            </div>
            <div>
              <Label htmlFor="code">Role Code</Label>
              <Input
                id="code"
                value={newRole.code}
                onChange={(e) => setNewRole({ ...newRole, code: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                placeholder="e.g., custom_role"
                required
              />
            </div>
            <div>
              <Label htmlFor="color">Badge Color</Label>
              <Input
                id="color"
                type="color"
                value={newRole.color}
                onChange={(e) => setNewRole({ ...newRole, color: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="level">Hierarchy Level</Label>
              <Input
                id="level"
                type="number"
                min="11"
                value={newRole.level}
                onChange={(e) => setNewRole({ ...newRole, level: parseInt(e.target.value) })}
              />
              <p className="text-xs text-muted-foreground mt-1">System roles use levels 1-10</p>
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={newRole.description}
                onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
                required
              />
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