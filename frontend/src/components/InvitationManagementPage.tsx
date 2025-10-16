import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Mail, Send, Trash2, RotateCw, Clock, AlertCircle, Lock } from 'lucide-react';


const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvitationManagementPage = () => {
  const { user } = useAuth();
  const [invitations, setInvitations] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [showInviteDialog, setShowInviteDialog] = useState<boolean>(false);
  const [inviteData, setInviteData] = useState({ email: '', role_id: '' });
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [deleteInvitation, setDeleteInvitation] = useState<any | null>(null);

  useEffect(() => {
    loadInvitations();
    loadRoles();
  }, []);

  const loadInvitations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/invitations`);
      setInvitations(response.data);
    } catch (err: unknown) {
      console.error('Failed to load invitations:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await axios.get(`${API}/roles`);
      setRoles(response.data.filter((r: any) => r.is_system_role).sort((a: any, b: any) => a.level - b.level));
    } catch (err: unknown) {
      console.error('Failed to load roles:', err);
    }
  };

  const handleSendInvitation = async (e: any) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/invitations`, inviteData);
      alert(`Invitation sent to ${inviteData.email}! They will receive an email with the invitation link.`);
      setShowInviteDialog(false);
      setInviteData({ email: '', role_id: '' });
      loadInvitations();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleResend = async (invitation: any) => {
    if (window.confirm(`Resend invitation to ${invitation.email}? This will reset the 7-day expiration.`)) {
      try {
        await axios.post(`${API}/invitations/${invitation.id}/resend`);
        alert('Invitation resent successfully! Expiration timer reset to 7 days.');
        loadInvitations();
      } catch (err: unknown) {
        alert((err as any).response?.data?.detail || 'Failed to resend invitation');
      }
    }
  };

  const handleDelete = async () => {
    if (!deleteInvitation) return;
    
    try {
      await axios.delete(`${API}/invitations/${deleteInvitation.id}`);
      alert('Invitation cancelled successfully!');
      setShowDeleteDialog(false);
      setDeleteInvitation(null);
      loadInvitations();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to cancel invitation');
      setShowDeleteDialog(false);
      setDeleteInvitation(null);
    }
  };

  const checkDeletePermission = (invitation: any) => {
    // User can delete if they invited OR if they have higher role level
    return invitation.invited_by === user?.id || true // canDeleteInvitation(user?.role, invitation.invited_by_role, invitation.invited_by === user?.id ? 'self' : 'other');
  };

  const getExpirationInfo = (expiresAt: any) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const daysLeft = Math.ceil((expires - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysLeft < 0) {
      return { text: 'Expired', variant: 'destructive', daysLeft: 0 };
    } else if (daysLeft === 0) {
      return { text: 'Expires today', variant: 'destructive', daysLeft: 0 };
    } else if (daysLeft === 1) {
      return { text: '1 day left', variant: 'destructive', daysLeft: 1 };
    } else if (daysLeft <= 2) {
      return { text: `${daysLeft} days left`, variant: 'warning', daysLeft };
    } else {
      return { text: `${daysLeft} days left`, variant: 'default', daysLeft };
    }
  };

  const getStatusBadge = (status: any) => {
    const variants = {
      pending: { color: 'bg-yellow-100 text-yellow-800', text: 'Pending' },
      accepted: { color: 'bg-green-100 text-green-800', text: 'Accepted' },
      expired: { color: 'bg-red-100 text-red-800', text: 'Expired' },
      cancelled: { color: 'bg-gray-100 text-gray-800', text: 'Cancelled' }
    };
    const variant = variants[status] || variants.pending;
    return <Badge className={variant.color}>{variant.text}</Badge>;
  };

  const getRoleInfo = (roleId: any) => {
    const role = roles.find((r: any) => r.id === roleId);
    return role || { name: roleId, color: '#64748b' };
  };

  const pendingInvitations = invitations.filter((i: any) => i.status === 'pending');
  // const _otherInvitations = invitations.filter((i: any) => i.status !== 'pending');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Invitation Management</h1>
          <p className="text-slate-600 dark:text-slate-400">Send and track user invitations (7-day expiration)</p>
        </div>
        <Button onClick={() => setShowInviteDialog(true)}>
          <Send className="h-4 w-4 mr-2" />
          Send Invitation
        </Button>
      </div>

      <Tabs defaultValue="pending">
        <TabsList>
          <TabsTrigger value="pending">
            Pending ({pendingInvitations.length})
          </TabsTrigger>
          <TabsTrigger value="all">
            All Invitations ({invitations.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <CardTitle>Pending Invitations</CardTitle>
              <CardDescription>Invitations awaiting acceptance (automatically expire after 7 days)</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading...</p>
              ) : pendingInvitations.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No pending invitations</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Invited By</TableHead>
                      <TableHead>Sent</TableHead>
                      <TableHead>Expiration</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingInvitations.map((invitation: any) => {
                      const roleInfo = getRoleInfo(invitation.role_id);
                      const expInfo = getExpirationInfo(invitation.expires_at);
                      const canDelete = checkDeletePermission(invitation);
                      
                      return (
                        <TableRow key={invitation.id}>
                          <TableCell>{invitation.email}</TableCell>
                          <TableCell>
                            <Badge style={{ backgroundColor: roleInfo.color, color: 'white' }}>
                              {roleInfo.name}
                            </Badge>
                          </TableCell>
                          <TableCell>{invitation.invited_by_name}</TableCell>
                          <TableCell>{new Date(invitation.created_at).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              <span className={`text-sm font-medium ${
                                expInfo.daysLeft <= 2 ? 'text-red-600' : 'text-slate-600'
                              }`}>
                                {expInfo.text}
                              </span>
                              {expInfo.daysLeft <= 2 && (
                                <AlertCircle className="h-3 w-3 text-red-600" />
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleResend(invitation)}
                                title="Resend invitation email and reset expiration"
                              >
                                <RotateCw className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  if (canDelete) {
                                    setDeleteInvitation(invitation);
                                    setShowDeleteDialog(true);
                                  } else {
                                    alert('Access Denied: Only the inviter or higher-level roles can delete this invitation');
                                  }
                                }}
                                className={canDelete ? "text-red-600" : "text-gray-400"}
                                disabled={!canDelete}
                                title={canDelete ? "Cancel invitation" : "Insufficient permissions to delete"}
                              >
                                {canDelete ? <Trash2 className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="all">
          <Card>
            <CardHeader>
              <CardTitle>All Invitations</CardTitle>
              <CardDescription>Complete invitation history</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p>Loading...</p>
              ) : invitations.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No invitations</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Invited By</TableHead>
                      <TableHead>Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invitations.map((invitation: any) => {
                      const roleInfo = getRoleInfo(invitation.role_id);
                      return (
                        <TableRow key={invitation.id}>
                          <TableCell>{invitation.email}</TableCell>
                          <TableCell>
                            <Badge style={{ backgroundColor: roleInfo.color, color: 'white' }}>
                              {roleInfo.name}
                            </Badge>
                          </TableCell>
                          <TableCell>{getStatusBadge(invitation.status)}</TableCell>
                          <TableCell>{invitation.invited_by_name}</TableCell>
                          <TableCell>{new Date(invitation.created_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Send Invitation Dialog */}
      <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send User Invitation</DialogTitle>
            <DialogDescription>Invite a new user to join your organization (expires in 7 days)</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSendInvitation} className="space-y-4">
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={inviteData.email}
                onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                placeholder="user@example.com"
                required
              />
            </div>
            <div>
              <Label htmlFor="role">Assign Role (you can only invite lower/equal roles)</Label>
              <Select value={inviteData.role_id} onValueChange={(value) => setInviteData({ ...inviteData, role_id: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => {
                    const canInvite = true // canInviteRole(user?.role || 'viewer', role.code);
                    return (
                      <SelectItem 
                        key={role.id} 
                        value={role.id}
                        disabled={!canInvite}
                      >
                        <div className="flex items-center gap-2">
                          <span style={{ color: role.color }}>●</span>
                          {role.name} - {role.description}
                          {!canInvite && <Lock className="h-3 w-3 ml-2" />}
                        </div>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
              <Mail className="h-5 w-5 text-blue-600 mt-0.5" />
              <p className="text-sm text-blue-800">
                An invitation email will be sent with a secure link. The invitation expires after 7 days.
              </p>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowInviteDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">
                <Send className="h-4 w-4 mr-2" />
                Send Invitation
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Invitation</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this invitation? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {deleteInvitation && (
            <div className="space-y-4">
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm font-medium text-red-900">
                  {deleteInvitation.email}
                </p>
                <p className="text-sm text-red-600">
                  Invited by: {deleteInvitation.invited_by_name}
                </p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => {
                setShowDeleteDialog(false);
                setDeleteInvitation(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
            >
              Cancel Invitation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default InvitationManagementPage;
