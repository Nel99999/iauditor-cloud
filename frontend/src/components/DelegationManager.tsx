import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Plus, UserCheck, UserX, Calendar, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DelegationManager = () => {
  const { user } = useAuth();
  const [delegations, setDelegations] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  
  const [formData, setFormData] = useState({
    delegate_id: '',
    workflow_types: [],
    resource_types: [],
    valid_from: '',
    valid_until: '',
    reason: ''
  });

  useEffect(() => {
    loadDelegations();
    loadUsers();
  }, []);

  const loadDelegations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/context-permissions/delegations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDelegations(response.data);
    } catch (err: unknown) {
      console.error('Failed to load delegations:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data.filter((u: any) => u.id !== user?.id)); // Exclude self
    } catch (err: unknown) {
      console.error('Failed to load users:', err);
    }
  };

  const handleCreateDelegation = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/context-permissions/delegations`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowCreateDialog(false);
      resetForm();
      loadDelegations();
      alert('Delegation created successfully!');
    } catch (err: unknown) {
      console.error('Failed to create delegation:', err);
      alert((err as any).response?.data?.detail || 'Failed to create delegation');
    }
  };

  const handleRevokeDelegation = async (delegationId) => {
    if (!window.confirm('Are you sure you want to revoke this delegation?')) return;
    
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/context-permissions/delegations/${delegationId}/revoke`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadDelegations();
      alert('Delegation revoked successfully!');
    } catch (err: unknown) {
      console.error('Failed to revoke delegation:', err);
      alert((err as any).response?.data?.detail || 'Failed to revoke delegation');
    }
  };

  const resetForm = () => {
    const today = new Date().toISOString().split('T')[0];
    const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    setFormData({
      delegate_id: '',
      workflow_types: [],
      resource_types: [],
      valid_from: today,
      valid_until: nextWeek,
      reason: ''
    });
  };

  const formatDate = (dateStr: any) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const isActive = (delegation: any) => {
    const now = new Date().toISOString();
    return delegation.active && 
           delegation.valid_from <= now && 
           delegation.valid_until >= now;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Delegation Manager</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Delegate your approval authority to other users temporarily
          </p>
        </div>
        <Button onClick={() => { resetForm(); setShowCreateDialog(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          New Delegation
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-slate-600 dark:text-slate-400">Loading delegations...</p>
        </div>
      ) : delegations.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <UserCheck className="h-12 w-12 mx-auto mb-4 text-slate-400" />
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              No delegations yet. Create your first delegation!
            </p>
            <Button onClick={() => { resetForm(); setShowCreateDialog(true); }}>
              <Plus className="h-4 w-4 mr-2" />
              Create Delegation
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {delegations.map((delegation: any) => (
            <Card key={delegation.id} className={!isActive(delegation) ? 'opacity-60' : ''}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-lg">
                        {delegation.delegator_id === user?.id ? (
                          <span className="flex items-center gap-2">
                            <UserCheck className="h-5 w-5" />
                            You → {delegation.delegate_name}
                          </span>
                        ) : (
                          <span className="flex items-center gap-2">
                            <UserX className="h-5 w-5" />
                            {delegation.delegator_name} → You
                          </span>
                        )}
                      </CardTitle>
                      {isActive(delegation) ? (
                        <Badge className="bg-green-100 text-green-700">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-gray-600">
                          <XCircle className="h-3 w-3 mr-1" />
                          Inactive
                        </Badge>
                      )}
                    </div>
                    <CardDescription>{delegation.reason}</CardDescription>
                  </div>
                  {delegation.delegator_id === user?.id && isActive(delegation) && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleRevokeDelegation(delegation.id)}
                    >
                      Revoke
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Valid From</div>
                      <div className="font-medium">{formatDate(delegation.valid_from)}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Valid Until</div>
                      <div className="font-medium">{formatDate(delegation.valid_until)}</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Scope</div>
                    <div className="font-medium">
                      {delegation.workflow_types.length === 0 && delegation.resource_types.length === 0 ? (
                        <span className="text-blue-600">All workflows & resources</span>
                      ) : (
                        <span>
                          {delegation.workflow_types.length > 0 && `${delegation.workflow_types.length} workflows`}
                          {delegation.workflow_types.length > 0 && delegation.resource_types.length > 0 && ', '}
                          {delegation.resource_types.length > 0 && `${delegation.resource_types.length} resources`}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Delegation Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={(open) => {
        setShowCreateDialog(open);
        if (!open) resetForm();
      }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Delegation</DialogTitle>
            <DialogDescription>
              Temporarily delegate your approval authority to another user
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label>Delegate To</Label>
              <Select
                value={formData.delegate_id}
                onValueChange={(value) => setFormData({ ...formData, delegate_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a user" />
                </SelectTrigger>
                <SelectContent>
                  {users.map((u: any) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.name} ({u.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Valid From</Label>
                <Input
                  type="date"
                  value={formData.valid_from}
                  onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })}
                />
              </div>
              <div>
                <Label>Valid Until</Label>
                <Input
                  type="date"
                  value={formData.valid_until}
                  onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                />
              </div>
            </div>

            <div>
              <Label>Reason</Label>
              <Textarea
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="e.g., On vacation, Out sick, etc."
                rows={3}
              />
            </div>

            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Note:</strong> This delegation will grant the selected user the same approval
                authority as you for all workflows during the specified period. You can revoke it
                at any time.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateDialog(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateDelegation}
              disabled={!formData.delegate_id || !formData.reason}
            >
              Create Delegation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DelegationManager;