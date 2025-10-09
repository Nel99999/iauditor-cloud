import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Mail, Send, XCircle, RotateCw, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvitationManagementPage = () => {
  const [invitations, setInvitations] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [inviteData, setInviteData] = useState({ email: '', role_id: '' });

  useEffect(() => {
    loadInvitations();
    loadRoles();
  }, []);

  const loadInvitations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/invitations`);
      setInvitations(response.data);
    } catch (err) {
      console.error('Failed to load invitations:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await axios.get(`${API}/roles`);
      setRoles(response.data);
    } catch (err) {
      console.error('Failed to load roles:', err);
    }
  };

  const handleSendInvitation = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/invitations`, inviteData);
      alert(`Invitation sent to ${inviteData.email}!`);
      setShowInviteDialog(false);
      setInviteData({ email: '', role_id: '' });
      loadInvitations();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleResend = async (invitationId) => {
    try {
      await axios.post(`${API}/invitations/${invitationId}/resend`);
      alert('Invitation resent successfully!');
      loadInvitations();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to resend invitation');
    }
  };

  const handleCancel = async (invitationId) => {
    if (window.confirm('Cancel this invitation?')) {
      try {
        await axios.delete(`${API}/invitations/${invitationId}`);
        alert('Invitation cancelled successfully!');
        loadInvitations();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to cancel invitation');
      }
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: { color: 'bg-yellow-100 text-yellow-800', text: 'Pending' },
      accepted: { color: 'bg-green-100 text-green-800', text: 'Accepted' },
      expired: { color: 'bg-red-100 text-red-800', text: 'Expired' },
      cancelled: { color: 'bg-gray-100 text-gray-800', text: 'Cancelled' }
    };
    const variant = variants[status] || variants.pending;
    return <Badge className={variant.color}>{variant.text}</Badge>;
  };

  const pendingInvitations = invitations.filter(i => i.status === 'pending');
  const otherInvitations = invitations.filter(i => i.status !== 'pending');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Invitation Management</h1>
          <p className="text-slate-600 dark:text-slate-400">Send and track user invitations</p>
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
              <CardDescription>Invitations awaiting acceptance</CardDescription>
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
                      <TableHead>Expires</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingInvitations.map((invitation) => (
                      <TableRow key={invitation.id}>
                        <TableCell>{invitation.email}</TableCell>
                        <TableCell>
                          {(() => {
                            const role = roles.find(r => r.id === invitation.role_id);
                            return role ? (
                              <Badge style={{ backgroundColor: role.color, color: 'white' }}>
                                {role.name}
                              </Badge>
                            ) : (
                              <Badge>{invitation.role_id}</Badge>
                            );
                          })()}
                        </TableCell>
                        <TableCell>{invitation.invited_by_name}</TableCell>
                        <TableCell>{new Date(invitation.created_at).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {new Date(invitation.expires_at).toLocaleDateString()}
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleResend(invitation.id)}
                            >
                              <RotateCw className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleCancel(invitation.id)}
                              className="text-red-600"
                            >
                              <XCircle className="h-4 w-4" />
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
                    {invitations.map((invitation) => (
                      <TableRow key={invitation.id}>
                        <TableCell>{invitation.email}</TableCell>
                        <TableCell>
                          {(() => {
                            const role = roles.find(r => r.id === invitation.role_id);
                            return role ? (
                              <Badge style={{ backgroundColor: role.color, color: 'white' }}>
                                {role.name}
                              </Badge>
                            ) : (
                              <Badge>{invitation.role_id}</Badge>
                            );
                          })()}
                        </TableCell>
                        <TableCell>{getStatusBadge(invitation.status)}</TableCell>
                        <TableCell>{invitation.invited_by_name}</TableCell>
                        <TableCell>{new Date(invitation.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
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
            <DialogDescription>Invite a new user to join your organization</DialogDescription>
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
              <Label htmlFor="role">Assign Role</Label>
              <Select value={inviteData.role_id} onValueChange={(value) => setInviteData({ ...inviteData, role_id: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.id}>
                      {role.name} - {role.description}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
    </div>
  );
};

export default InvitationManagementPage;