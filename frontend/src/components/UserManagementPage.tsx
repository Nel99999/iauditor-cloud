// @ts-nocheck
import { useState, useEffect } from 'react';
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
import { UserPlus, Search, Mail, Shield, Eye, Trash2, Edit, Lock } from 'lucide-react';


const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagementPage = () => {
  // const { user } = useAuth();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showInviteDialog, setShowInviteDialog] = useState<boolean>(false);
  const [showEditDialog, setShowEditDialog] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [inviteData, setInviteData] = useState({ email: '', role: 'viewer' });
  const [editUserData, setEditUserData] = useState<any | null>(null);
  const [deleteUserData, setDeleteUserData] = useState<any | null>(null);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (err: unknown) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: any) => {
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
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleSort = (column: any) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const filteredUsers = users
    .filter(
      (u) =>
        u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.role.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a: any, b: any) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'name':
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case 'role':
          aVal = a.role.toLowerCase();
          bVal = b.role.toLowerCase();
          break;
        case 'status':
          aVal = a.status.toLowerCase();
          bVal = b.status.toLowerCase();
          break;
        case 'last_login':
          aVal = a.last_login || '';
          bVal = b.last_login || '';
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  const getRoleBadgeStyle = (role: any) => {
    switch (role) {
      case 'developer':
        return { backgroundColor: '#6366f1', color: 'white', borderColor: '#6366f1' }; // Indigo
      case 'master':
        return { backgroundColor: '#9333ea', color: 'white', borderColor: '#9333ea' }; // Purple
      case 'admin':
        return { backgroundColor: '#ef4444', color: 'white', borderColor: '#ef4444' }; // Red
      case 'operations_manager':
        return { backgroundColor: '#f59e0b', color: 'white', borderColor: '#f59e0b' }; // Amber
      case 'team_lead':
        return { backgroundColor: '#06b6d4', color: 'white', borderColor: '#06b6d4' }; // Cyan
      case 'manager':
        return { backgroundColor: '#3b82f6', color: 'white', borderColor: '#3b82f6' }; // Blue
      case 'supervisor':
        return { backgroundColor: '#14b8a6', color: 'white', borderColor: '#14b8a6' }; // Teal
      case 'inspector':
        return { backgroundColor: '#eab308', color: 'white', borderColor: '#eab308' }; // Yellow
      case 'operator':
        return { backgroundColor: '#64748b', color: 'white', borderColor: '#64748b' }; // Slate
      case 'viewer':
        return { backgroundColor: '#bef264', color: 'black', borderColor: '#bef264' }; // Bright Neon Lime
      default:
        return { backgroundColor: '#64748b', color: 'white', borderColor: '#64748b' }; // Slate
    }
  };

  const getInitials = (name: any) => {
    return name
      .split(' ')
      .map((n: any) => n[0])
      .join('')
      .toUpperCase();
  };

  const formatDate = (dateString: any) => {
    if (!dateString || dateString === 'Recently') return 'Never';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-ZA', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e: unknown) {
      return dateString;
    }
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
                  <TableHead 
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => handleSort('name')}
                  >
                    User {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => handleSort('role')}
                  >
                    Role {sortBy === 'role' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => handleSort('status')}
                  >
                    Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => handleSort('last_login')}
                  >
                    Last Login {sortBy === 'last_login' && (sortOrder === 'asc' ? '↑' : '↓')}
                  </TableHead>
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
                      <Badge style={getRoleBadgeStyle(u.role)} className="capitalize">
                        {u.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={u.status === 'active' ? 'default' : 'secondary'}>
                        {u.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(u.last_login)}
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
                          onClick={() => {
                            setDeleteUserData(u);
                            setShowDeleteDialog(true);
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete User</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this user? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {deleteUserData && (
            <div className="space-y-4">
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm font-medium text-red-900">
                  {deleteUserData.name}
                </p>
                <p className="text-sm text-red-600">
                  {deleteUserData.email}
                </p>
              </div>
              <p className="text-sm text-muted-foreground">
                This user will be removed from the system and will no longer have access.
              </p>
            </div>
          )}
          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => {
                setShowDeleteDialog(false);
                setDeleteUserData(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (!deleteUserData) return;
                
                try {
                  setLoading(true);
                  await axios.delete(`${API}/users/${deleteUserData.id}`);
                  alert('User deleted successfully!');
                  setShowDeleteDialog(false);
                  setDeleteUserData(null);
                  loadUsers();
                } catch (err: unknown) {
                  alert((err as any).response?.data?.detail || 'Failed to delete user');
                } finally {
                  setLoading(false);
                }
              }}
              disabled={loading}
            >
              {loading ? 'Deleting...' : 'Delete User'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
                    <SelectItem value="developer">🔵 Developer - Software Owner (Lv1)</SelectItem>
                    <SelectItem value="master">🟣 Master - Business Owner (Lv2)</SelectItem>
                    <SelectItem value="admin">🔴 Admin - Organization Admin (Lv3)</SelectItem>
                    <SelectItem value="operations_manager">🟠 Operations Manager - Strategic (Lv4)</SelectItem>
                    <SelectItem value="team_lead">🔵 Team Lead - Lead teams (Lv5)</SelectItem>
                    <SelectItem value="manager">🔵 Manager - Branch/Dept management (Lv6)</SelectItem>
                    <SelectItem value="supervisor">🩵 Supervisor - Supervise shifts (Lv7)</SelectItem>
                    <SelectItem value="inspector">🟡 Inspector - Execute operations (Lv8)</SelectItem>
                    <SelectItem value="operator">⚫ Operator - Basic tasks (Lv9)</SelectItem>
                    <SelectItem value="viewer">🟢 Viewer - Read only (Lv10)</SelectItem>
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
                } catch (err: unknown) {
                  alert((err as any).response?.data?.detail || 'Failed to update user');
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
                <Label htmlFor="invite-role">Role (you can only invite lower/equal roles)</Label>
                <Select
                  value={inviteData.role}
                  onValueChange={(value) => setInviteData({ ...inviteData, role: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[
                      { value: 'developer', label: '🔵 Developer - Software Owner (Lv1)', emoji: '🔵' },
                      { value: 'master', label: '🟣 Master - Business Owner (Lv2)', emoji: '🟣' },
                      { value: 'admin', label: '🔴 Admin - Organization Admin (Lv3)', emoji: '🔴' },
                      { value: 'operations_manager', label: '🟠 Operations Manager - Strategic (Lv4)', emoji: '🟠' },
                      { value: 'team_lead', label: '🔵 Team Lead - Lead teams (Lv5)', emoji: '🔵' },
                      { value: 'manager', label: '🔵 Manager - Branch/Dept management (Lv6)', emoji: '🔵' },
                      { value: 'supervisor', label: '🩵 Supervisor - Supervise shifts (Lv7)', emoji: '🩵' },
                      { value: 'inspector', label: '🟡 Inspector - Execute operations (Lv8)', emoji: '🟡' },
                      { value: 'operator', label: '⚫ Operator - Basic tasks (Lv9)', emoji: '⚫' },
                      { value: 'viewer', label: '🟢 Viewer - Read only (Lv10)', emoji: '🟢' },
                    ].map((role: any) => {
                      const canInvite = true // canInviteRole(user?.role || 'viewer', role.value);
                      return (
                        <SelectItem 
                          key={role.value} 
                          value={role.value}
                          disabled={!canInvite}
                        >
                          <div className="flex items-center gap-2">
                            {role.label}
                            {!canInvite && <Lock className="h-3 w-3" />}
                          </div>
                        </SelectItem>
                      );
                    })}
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