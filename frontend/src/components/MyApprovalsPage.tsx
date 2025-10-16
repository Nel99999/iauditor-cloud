import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { CheckCircle2, XCircle, AlertCircle, Clock, FileText, User, Calendar, MessageSquare } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MyApprovalsPage = () => {
  const { user } = useAuth();
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [showActionDialog, setShowActionDialog] = useState<boolean>(false);
  const [action, setAction] = useState<string>('');
  const [comments, setComments] = useState<string>('');
  const [processing, setProcessing] = useState<boolean>(false);

  useEffect(() => {
    loadApprovals();
    // Poll for new approvals every 30 seconds
    const interval = setInterval(loadApprovals, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadApprovals = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/workflows/instances/my-approvals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApprovals(response.data);
    } catch (err: unknown) {
      console.error('Failed to load approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalAction = async () => {
    if (!action) return;

    setProcessing(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API}/workflows/instances/${selectedWorkflow.id}/approve`,
        { action, comments },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setShowActionDialog(false);
      setSelectedWorkflow(null);
      setComments('');
      setAction('');
      loadApprovals();
      
      const actionText = action === 'approve' ? 'approved' : action === 'reject' ? 'rejected' : 'changes requested';
      alert(`Workflow ${actionText} successfully!`);
    } catch (err: unknown) {
      console.error('Failed to process approval:', err);
      alert((err as any).response?.data?.detail || 'Failed to process approval');
    } finally {
      setProcessing(false);
    }
  };

  const openActionDialog = (workflow, actionType) => {
    setSelectedWorkflow(workflow);
    setAction(actionType);
    setShowActionDialog(true);
  };

  const getStatusColor = (status: any) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      case 'in_progress': return 'bg-blue-100 text-blue-700';
      case 'escalated': return 'bg-orange-100 text-orange-700';
      case 'cancelled': return 'bg-gray-100 text-gray-700';
      default: return 'bg-yellow-100 text-yellow-700';
    }
  };

  const formatDate = (dateStr: any) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString();
  };

  const isOverdue = (dueDate: any) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">My Approvals</h2>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Workflows pending your approval
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-slate-600 dark:text-slate-400">Loading approvals...</p>
        </div>
      ) : approvals.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-green-500" />
            <p className="text-slate-600 dark:text-slate-400">
              No pending approvals. You're all caught up!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((workflow: any) => (
            <Card key={workflow.id} className={isOverdue(workflow.due_at) ? 'border-red-300 bg-red-50 dark:bg-red-950/20' : ''}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-lg">{workflow.template_name}</CardTitle>
                      <Badge className={getStatusColor(workflow.status)}>
                        {workflow.status}
                      </Badge>
                      {workflow.status === 'escalated' && (
                        <Badge variant="outline" className="text-orange-700 border-orange-300">
                          ⚡ Escalated
                        </Badge>
                      )}
                      {isOverdue(workflow.due_at) && (
                        <Badge variant="outline" className="text-red-700 border-red-300">
                          ⏰ Overdue
                        </Badge>
                      )}
                    </div>
                    <CardDescription>
                      <span className="font-semibold">{workflow.resource_type}</span>: {workflow.resource_name}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="bg-green-50 hover:bg-green-100 text-green-700 border-green-300"
                      onClick={() => openActionDialog(workflow, 'approve')}
                      disabled={processing}
                    >
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="bg-red-50 hover:bg-red-100 text-red-700 border-red-300"
                      onClick={() => openActionDialog(workflow, 'reject')}
                      disabled={processing}
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openActionDialog(workflow, 'request_changes')}
                      disabled={processing}
                    >
                      <AlertCircle className="h-4 w-4 mr-1" />
                      Request Changes
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Created By</div>
                      <div className="font-medium">{workflow.created_by_name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Started</div>
                      <div className="font-medium">{formatDate(workflow.started_at).split(' ')[0]}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Due</div>
                      <div className={`font-medium ${isOverdue(workflow.due_at) ? 'text-red-600' : ''}`}>
                        {formatDate(workflow.due_at).split(' ')[0]}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-slate-500" />
                    <div>
                      <div className="text-xs text-slate-500">Current Step</div>
                      <div className="font-medium">Step {workflow.current_step}</div>
                    </div>
                  </div>
                </div>

                {workflow.steps_completed && workflow.steps_completed.length > 0 && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-xs font-semibold text-slate-700 mb-2">Previous Steps:</p>
                    <div className="space-y-2">
                      {workflow.steps_completed.map((step: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-2 text-xs">
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center text-white ${
                            step.action === 'approve' ? 'bg-green-500' :
                            step.action === 'reject' ? 'bg-red-500' : 'bg-yellow-500'
                          }`}>
                            {step.action === 'approve' ? '✓' : step.action === 'reject' ? '✕' : '!'}
                          </div>
                          <div className="flex-1">
                            <div className="font-medium">
                              {step.step_name} - {step.action}
                            </div>
                            <div className="text-slate-500">
                              By {step.approved_by_name} on {formatDate(step.approved_at)}
                            </div>
                            {step.comments && (
                              <div className="text-slate-600 italic mt-1">"{step.comments}"</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Action Dialog */}
      <Dialog open={showActionDialog} onOpenChange={(open) => {
        setShowActionDialog(open);
        if (!open) {
          setSelectedWorkflow(null);
          setComments('');
          setAction('');
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {action === 'approve' ? 'Approve Workflow' :
               action === 'reject' ? 'Reject Workflow' :
               'Request Changes'}
            </DialogTitle>
            <DialogDescription>
              {selectedWorkflow && (
                <div className="mt-2">
                  <p><strong>Workflow:</strong> {selectedWorkflow.template_name}</p>
                  <p><strong>Resource:</strong> {selectedWorkflow.resource_type} - {selectedWorkflow.resource_name}</p>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Label>Comments {action !== 'approve' && <span className="text-red-500">*</span>}</Label>
            <Textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Add your comments here..."
              rows={4}
              className="mt-2"
            />
            {action !== 'approve' && !comments && (
              <p className="text-xs text-red-500 mt-1">Comments are required for rejection or change requests</p>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowActionDialog(false);
                setSelectedWorkflow(null);
                setComments('');
                setAction('');
              }}
              disabled={processing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleApprovalAction}
              disabled={processing || (action !== 'approve' && !comments)}
              className={
                action === 'approve' ? 'bg-green-600 hover:bg-green-700' :
                action === 'reject' ? 'bg-red-600 hover:bg-red-700' :
                'bg-yellow-600 hover:bg-yellow-700'
              }
            >
              {processing ? 'Processing...' : (
                action === 'approve' ? 'Approve' :
                action === 'reject' ? 'Reject' : 'Request Changes'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MyApprovalsPage;