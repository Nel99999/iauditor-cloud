import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle, XCircle, Clock, Mail, User as UserIcon } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

interface PendingUser {
  id: string;
  email: string;
  name: string;
  created_at: string;
  organization_id: string;
  role: string;
  registration_ip?: string;
}

const UserApprovalPage: React.FC = () => {
  const { toast } = useToast();
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<PendingUser | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [notes, setNotes] = useState('');
  const [showDialog, setShowDialog] = useState(false);

  const fetchPendingUsers = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const response = await axios.get(`${BACKEND_URL}/api/users/pending-approvals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingUsers(response.data);
    } catch (error: any) {
      console.error('Error fetching pending users:', error);
      if (error.response?.status === 403) {
        toast({
          title: 'Access Denied',
          description: 'You do not have permission to view pending approvals.'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingUsers();
  }, []);

  const handleAction = (userToAction: PendingUser, type: 'approve' | 'reject') => {
    setSelectedUser(userToAction);
    setActionType(type);
    setNotes('');
    setShowDialog(true);
  };

  const confirmAction = async () => {
    if (!selectedUser || !actionType) return;

    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const endpoint = actionType === 'approve' ? 'approve' : 'reject';
      
      await axios.post(
        `${BACKEND_URL}/api/users/${selectedUser.id}/${endpoint}`,
        { approval_notes: notes },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast({
        title: actionType === 'approve' ? 'User Approved' : 'User Rejected',
        description: `${selectedUser.email} has been ${actionType}d successfully.`
      });

      setShowDialog(false);
      setSelectedUser(null);
      setNotes('');
      fetchPendingUsers(); // Refresh list
    } catch (error: any) {
      console.error(`Error ${actionType}ing user:`, error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || `Failed to ${actionType} user`
      });
    }
  };

  const getDaysAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays === 0 ? 'Today' : `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading pending approvals...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">User Approvals</h1>
        <p className="text-gray-400 mt-2">
          Review and approve pending user registrations
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-500/10 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-500" />
              </div>
              <div>
                <p className="text-sm text-gray-400">Pending Approval</p>
                <p className="text-2xl font-bold text-gray-100">{pendingUsers.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Users List */}
      {pendingUsers.length === 0 ? (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardContent className="p-12 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-100 mb-2">
              No Pending Approvals
            </h3>
            <p className="text-gray-400">
              All user registrations have been processed.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-gray-100">Pending User Registrations</CardTitle>
            <CardDescription className="text-gray-400">
              Review and approve or reject user registrations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingUsers.map((pendingUser) => (
                <div
                  key={pendingUser.id}
                  className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg border border-gray-700"
                >
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-500/10 rounded">
                        <UserIcon className="h-5 w-5 text-blue-400" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-100">{pendingUser.name}</h4>
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <Mail className="h-4 w-4" />
                          {pendingUser.email}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-400 ml-12">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        Registered {getDaysAgo(pendingUser.created_at)}
                      </div>
                      <Badge variant="outline" className="text-gray-400 border-gray-600">
                        {pendingUser.role}
                      </Badge>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleAction(pendingUser, 'approve')}
                      className="bg-green-500/10 border-green-500/20 text-green-400 hover:bg-green-500/20"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAction(pendingUser, 'reject')}
                      className="bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20"
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Confirmation Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="bg-gray-800 border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-gray-100">
              {actionType === 'approve' ? 'Approve User' : 'Reject User'}
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              {actionType === 'approve' 
                ? 'Approve this user to grant them access to your organization.'
                : 'Reject this user registration. They will be notified of the rejection.'}
            </DialogDescription>
          </DialogHeader>

          {selectedUser && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <p className="text-sm text-gray-400">User</p>
                <p className="font-semibold text-gray-100">{selectedUser.name}</p>
                <p className="text-sm text-gray-400">{selectedUser.email}</p>
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-2">
                  Notes {actionType === 'reject' && <span className="text-red-400">(Required)</span>}
                </label>
                <Textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={actionType === 'approve' ? 'Optional approval notes...' : 'Please provide a reason for rejection...'}
                  className="bg-gray-900 border-gray-700 text-gray-100"
                  rows={3}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowDialog(false);
                setSelectedUser(null);
                setNotes('');
              }}
              className="border-gray-700 text-gray-400"
            >
              Cancel
            </Button>
            <Button
              onClick={confirmAction}
              disabled={actionType === 'reject' && !notes.trim()}
              className={actionType === 'approve' 
                ? 'bg-green-600 hover:bg-green-700' 
                : 'bg-red-600 hover:bg-red-700'}
            >
              {actionType === 'approve' ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve User
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject User
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserApprovalPage;
