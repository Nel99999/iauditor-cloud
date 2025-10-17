// @ts-nocheck
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '@/hooks/usePermissions';
import { ROLE_LEVELS } from '@/utils/permissions';
import { PermissionGuard } from '@/components/PermissionGuard';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
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
import { 
  UserPlus, Search, Mail, Shield, Eye, Trash2, Edit, Lock, 
  CheckCircle, XCircle, Clock, RefreshCw, Send
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagementPageNew = () => {
  const { user: currentUser } = useAuth();
  const { hasPermission, getRoleLevel } = usePermissions();
  
  // State for all tabs
  const [activeTab, setActiveTab] = useState('active-users');
  const [users, setUsers] = useState<any[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [pendingInvites, setPendingInvites] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  // Dialogs
  const [showInviteDialog, setShowInviteDialog] = useState<boolean>(false);
  const [showEditDialog, setShowEditDialog] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [showApprovalDialog, setShowApprovalDialog] = useState<boolean>(false);
  
  // Data
  const [inviteData, setInviteData] = useState({ email: '', role: 'viewer' });
  const [editUserData, setEditUserData] = useState<any | null>(null);
  const [deleteUserData, setDeleteUserData] = useState<any | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<any | null>(null);
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject' | null>(null);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadActiveUsers(),
        loadPendingApprovals(),
        loadPendingInvites()
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadActiveUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (err: unknown) {
      console.error('Failed to load users:', err);
    }
  };

  const loadPendingApprovals = async () => {
    try {
      // Only load if user has permission
      if (!hasPermission('user', 'approve', 'organization')) {
        setPendingApprovals([]);
        return;
      }
      
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const response = await axios.get(`${API}/users/pending-approvals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingApprovals(response.data);
    } catch (err: unknown) {
      console.error('Failed to load pending approvals:', err);
      setPendingApprovals([]);
    }
  };

  const loadPendingInvites = async () => {
    try {
      // Only load if user has permission
      if (!hasPermission('invitation', 'read', 'organization')) {
        setPendingInvites([]);
        return;
      }
      
      const response = await axios.get(`${API}/invitations/pending`);
      setPendingInvites(response.data);
    } catch (err: unknown) {
      console.error('Failed to load pending invites:', err);
      setPendingInvites([]);
    }
  };

  // Handlers
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
      loadData();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleApproval = async () => {
    if (!selectedApproval || !approvalAction) return;

    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const endpoint = approvalAction === 'approve' ? 'approve' : 'reject';
      
      await axios.post(
        `${API}/users/${selectedApproval.id}/${endpoint}`,
        { approval_notes: approvalNotes },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert(`User ${approvalAction}d successfully!`);
      setShowApprovalDialog(false);
      setSelectedApproval(null);
      setApprovalAction(null);
      setApprovalNotes('');
      loadData();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || `Failed to ${approvalAction} user`);
    }
  };

  const handleResendInvite = async (inviteId: string) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      await axios.post(`${API}/invitations/${inviteId}/resend`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Invitation resent successfully!');
      loadPendingInvites();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to resend invitation');
    }
  };

  const handleCancelInvite = async (inviteId: string) => {
    if (!confirm('Are you sure you want to cancel this invitation?')) return;
    
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      await axios.delete(`${API}/invitations/${inviteId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Invitation cancelled successfully!');
      loadPendingInvites();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to cancel invitation');
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

  const canManageUser = (targetUser: any) => {
    if (!currentUser) return false;
    
    const currentLevel = getRoleLevel();
    const targetLevel = (ROLE_LEVELS as any)[targetUser.role] || 999;
    
    // Can manage if current level is lower (higher authority) than target
    return currentLevel < targetLevel;
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
    const styles: any = {
      developer: { backgroundColor: '#6366f1', color: 'white' },
      master: { backgroundColor: '#9333ea', color: 'white' },
      admin: { backgroundColor: '#ef4444', color: 'white' },
      operations_manager: { backgroundColor: '#f59e0b', color: 'white' },
      team_lead: { backgroundColor: '#06b6d4', color: 'white' },
      manager: { backgroundColor: '#3b82f6', color: 'white' },
      supervisor: { backgroundColor: '#14b8a6', color: 'white' },
      inspector: { backgroundColor: '#eab308', color: 'white' },
      operator: { backgroundColor: '#64748b', color: 'white' },
      viewer: { backgroundColor: '#bef264', color: 'black' },
    };
    return styles[role] || { backgroundColor: '#64748b', color: 'white' };
  };

  const getInitials = (name: any) => {
    return name.split(' ').map((n: any) => n[0]).join('').toUpperCase();
  };

  const formatDate = (dateString: any) => {
    if (!dateString || dateString === 'Recently') return 'Never';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-ZA', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch (e: unknown) {
      return dateString;
    }
  };

  // Check tab permissions
  const canViewApprovals = hasPermission('user', 'approve', 'organization');
  const canViewInvites = hasPermission('invitation', 'read', 'organization');

  return (
    <ModernPageWrapper 
      title="User Management" 
      subtitle="Manage users, approvals, and invitations"
      actions={
        <PermissionGuard 
          anyPermissions={['invitation.create.organization', 'user.create.organization']}
          tooltipMessage="You don't have permission to invite users"
        >
          <Button onClick={() => setShowInviteDialog(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Invite User
          </Button>
        </PermissionGuard>
      }
    >
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
              <p className="text-xs text-muted-foreground">Active accounts</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pendingApprovals.length}</div>
              <p className="text-xs text-muted-foreground">Awaiting approval</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Invites</CardTitle>
              <Mail className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pendingInvites.length}</div>
              <p className="text-xs text-muted-foreground">Not yet accepted</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Admins</CardTitle>
              <Shield className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter((u) => ['developer', 'master', 'admin'].includes(u.role)).length}
              </div>
              <p className="text-xs text-muted-foreground">Admin users</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="active-users">
              Active Users ({users.length})
            </TabsTrigger>
            
            <TabsTrigger value="pending-approvals" disabled={!canViewApprovals}>
              Pending Approvals ({pendingApprovals.length})
              {!canViewApprovals && <Lock className="h-3 w-3 ml-2" />}
            </TabsTrigger>

            <TabsTrigger value="pending-invites" disabled={!canViewInvites}>
              Pending Invites ({pendingInvites.length})
              {!canViewInvites && <Lock className="h-3 w-3 ml-2" />}
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: Active Users */}
          <TabsContent value="active-users">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Active Users</CardTitle>
                    <CardDescription>All active and inactive user accounts</CardDescription>
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
                            <Badge variant={u.is_active ? 'default' : 'secondary'}>
                              {u.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <PermissionGuard
                                permission="user.update.organization"
                                tooltipMessage="No permission to edit users"
                              >
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  disabled={!canManageUser(u)}
                                  title={!canManageUser(u) ? "Cannot edit higher-level roles" : "Edit user"}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                              </PermissionGuard>

                              <PermissionGuard
                                permission="user.delete.organization"
                                tooltipMessage="No permission to delete users"
                              >
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  disabled={!canManageUser(u)}
                                  title={!canManageUser(u) ? "Cannot delete higher-level roles" : "Delete user"}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </PermissionGuard>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: Pending Approvals */}
          <TabsContent value="pending-approvals">
            <Card>
              <CardHeader>
                <CardTitle>Pending User Approvals</CardTitle>
                <CardDescription>
                  Users who registered and are waiting for approval
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pendingApprovals.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No pending approvals
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>User</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Registered</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pendingApprovals.map((approval) => (
                        <TableRow key={approval.id}>
                          <TableCell className="font-medium">{approval.name}</TableCell>
                          <TableCell>{approval.email}</TableCell>
                          <TableCell>{formatDate(approval.created_at)}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600"
                                onClick={() => {
                                  setSelectedApproval(approval);
                                  setApprovalAction('approve');
                                  setShowApprovalDialog(true);
                                }}
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Approve
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600"
                                onClick={() => {
                                  setSelectedApproval(approval);
                                  setApprovalAction('reject');
                                  setShowApprovalDialog(true);
                                }}
                              >
                                <XCircle className="h-4 w-4 mr-1" />
                                Reject
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
          </TabsContent>

          {/* TAB 3: Pending Invites */}
          <TabsContent value="pending-invites">
            <Card>
              <CardHeader>
                <CardTitle>Pending Invitations</CardTitle>
                <CardDescription>
                  Users invited but not yet accepted
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pendingInvites.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No pending invitations
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Email</TableHead>
                        <TableHead>Invited By</TableHead>
                        <TableHead>Sent</TableHead>
                        <TableHead>Expires</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pendingInvites.map((invite) => (
                        <TableRow key={invite.id}>
                          <TableCell className="font-medium">{invite.email}</TableCell>
                          <TableCell>{invite.invited_by_name}</TableCell>
                          <TableCell>{formatDate(invite.created_at)}</TableCell>
                          <TableCell>{formatDate(invite.expires_at)}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <PermissionGuard
                                permission="invitation.resend.organization"
                                tooltipMessage="No permission to resend invites"
                              >
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleResendInvite(invite.id)}
                                >
                                  <Send className="h-4 w-4 mr-1" />
                                  Resend
                                </Button>
                              </PermissionGuard>

                              <PermissionGuard
                                permission="invitation.cancel.organization"
                                tooltipMessage="No permission to cancel invites"
                              >
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="text-red-600"
                                  onClick={() => handleCancelInvite(invite.id)}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Cancel
                                </Button>
                              </PermissionGuard>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Approval Dialog */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {approvalAction === 'approve' ? 'Approve User' : 'Reject User'}
            </DialogTitle>
            <DialogDescription>
              {approvalAction === 'approve'
                ? `Approve ${selectedApproval?.name} to join the organization?`
                : `Reject ${selectedApproval?.name}'s registration?`}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Notes (Optional)</Label>
              <Textarea
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                placeholder="Add any notes about this decision..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowApprovalDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleApproval}
              variant={approvalAction === 'approve' ? 'default' : 'destructive'}
            >
              {approvalAction === 'approve' ? 'Approve' : 'Reject'}
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
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={inviteData.email}
                  onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <Select
                  value={inviteData.role}
                  onValueChange={(value) => setInviteData({ ...inviteData, role: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="viewer">Viewer</SelectItem>
                    <SelectItem value="operator">Operator</SelectItem>
                    <SelectItem value="inspector">Inspector</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
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
    </ModernPageWrapper>
  );
};

export default UserManagementPageNew;
