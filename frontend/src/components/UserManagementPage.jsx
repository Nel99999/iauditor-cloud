import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { UserPlus, Search, Mail, Shield, Eye, Trash2, Edit } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagementPage = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [inviteData, setInviteData] = useState({ email: '', role: 'viewer' });
  const [editUserData, setEditUserData] = useState(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/users/invite`, {
        email: inviteData.email,
        role: inviteData.role,
      });
      alert(`Invitation sent to ${inviteData.email}!`);
      setShowInviteDialog(false);
      setInviteData({ email: '', role: 'viewer' });
      loadUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const filteredUsers = users.filter(
    (u) =>
      u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadgeStyle = (role) => {
    switch (role) {
      case 'master':
        return { backgroundColor: '#9333ea', color: 'white', borderColor: '#9333ea' }; // Purple
      case 'admin':
        return { backgroundColor: '#ef4444', color: 'white', borderColor: '#ef4444' }; // Red
      case 'manager':
        return { backgroundColor: '#3b82f6', color: 'white', borderColor: '#3b82f6' }; // Blue
      case 'inspector':
        return { backgroundColor: '#eab308', color: 'white', borderColor: '#eab308' }; // Yellow
      case 'viewer':
        return { backgroundColor: '#22c55e', color: 'white', borderColor: '#22c55e' }; // Green
      default:
        return { backgroundColor: '#94a3b8', color: 'white', borderColor: '#94a3b8' }; // Gray
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            User Management
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage users, roles, and permissions across your organization
          </p>
        </div>
        <Button onClick={() => setShowInviteDialog(true)} data-testid="invite-user-btn">
          <UserPlus className="h-4 w-4 mr-2" />
          Invite User
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{users.length}</div>
            <p className="text-xs text-muted-foreground">Across all units</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {users.filter((u) => u.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">Currently active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Invites</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Awaiting acceptance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Admins</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {users.filter((u) => u.role === 'admin').length}
            </div>
            <p className="text-xs text-muted-foreground">Admin users</p>
          </CardContent>
        </Card>
      </div>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>All Users</CardTitle>
              <CardDescription>Manage user accounts and permissions</CardDescription>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading users...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={u.picture} alt={u.name} />
                          <AvatarFallback>{getInitials(u.name)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{u.name}</div>
                          <div className="text-sm text-muted-foreground">{u.email}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(u.role)} className="capitalize">
                        {u.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={u.status === 'active' ? 'default' : 'secondary'}>
                        {u.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {u.last_login}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => {
                            setEditUserData(u);
                            setShowEditDialog(true);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={async () => {
                            if (window.confirm(`Are you sure you want to delete ${u.name}? This action cannot be undone.`)) {
                              try {
                                await axios.delete(`${API}/users/${u.id}`);
                                alert('User deleted successfully!');
                                loadUsers();
                              } catch (err) {
                                alert(err.response?.data?.detail || 'Failed to delete user');
                              }
                            }
                          }}
                          className="text-red-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Edit User Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Update user role and status
            </DialogDescription>
          </DialogHeader>
          {editUserData && (
            <div className="space-y-4">
              <div>
                <Label>User</Label>
                <Input value={`${editUserData.name} (${editUserData.email})`} disabled />
              </div>
              <div>
                <Label htmlFor="edit-role">Role</Label>
                <Select
                  value={editUserData.role}
                  onValueChange={(value) => setEditUserData({ ...editUserData, role: value })}
                >
                  <SelectTrigger id="edit-role">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin - Full access</SelectItem>
                    <SelectItem value="manager">Manager - Manage teams</SelectItem>
                    <SelectItem value="inspector">Inspector - Execute operations</SelectItem>
                    <SelectItem value="viewer">Viewer - Read only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit-status">Status</Label>
                <Select
                  value={editUserData.status}
                  onValueChange={(value) => setEditUserData({ ...editUserData, status: value })}
                >
                  <SelectTrigger id="edit-status">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={async () => {
                try {
                  await axios.put(`${API}/users/${editUserData.id}`, {
                    role: editUserData.role,
                    status: editUserData.status,
                  });
                  alert('User updated successfully!');
                  setShowEditDialog(false);
                  loadUsers();
                } catch (err) {
                  alert(err.response?.data?.detail || 'Failed to update user');
                }
              }}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Invite Dialog */}
      <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite User</DialogTitle>
            <DialogDescription>
              Send an invitation to join your organization
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleInvite}>
            <div className="space-y-4">
              <div>
                <Label htmlFor="invite-email">Email Address</Label>
                <Input
                  id="invite-email"
                  type="email"
                  placeholder="user@example.com"
                  value={inviteData.email}
                  onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="invite-role">Role</Label>
                <Select
                  value={inviteData.role}
                  onValueChange={(value) => setInviteData({ ...inviteData, role: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin - Full access</SelectItem>
                    <SelectItem value="manager">Manager - Manage teams</SelectItem>
                    <SelectItem value="inspector">Inspector - Execute operations</SelectItem>
                    <SelectItem value="viewer">Viewer - Read only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter className="mt-4">
              <Button type="button" variant="outline" onClick={() => setShowInviteDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Send Invitation</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserManagementPage;