// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import TimeLoggingDialog from '@/components/TimeLoggingDialog';
import { ArrowLeft, Edit, Clock, Package, History, DollarSign, Wrench, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkOrderDetailPage = () => {
  const navigate = useNavigate();
  const { woId } = useParams();
  const [workOrder, setWorkOrder] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [showTimeDialog, setShowTimeDialog] = useState(false);
  const [showPartsDialog, setShowPartsDialog] = useState(false);
  const [partsData, setPartsData] = useState({ part_name: '', cost: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [woId]);

  const loadData = async () => {
    try {
      const [woRes, timelineRes] = await Promise.all([
        axios.get(`${API}/work-orders/${woId}`),
        axios.get(`${API}/work-orders/${woId}/timeline`),
      ]);
      setWorkOrder(woRes.data);
      setTimeline(timelineRes.data.timeline || []);
    } catch (err) {
      console.error('Failed to load work order:', err);
      navigate('/work-orders');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await axios.put(`${API}/work-orders/${woId}/status`, { status: newStatus });
      loadData();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const handleAddParts = async () => {
    try {
      await axios.post(`${API}/work-orders/${woId}/add-parts`, {
        part_name: partsData.part_name,
        cost: parseFloat(partsData.cost),
      });
      setShowPartsDialog(false);
      setPartsData({ part_name: '', cost: '' });
      loadData();
    } catch (err) {
      alert('Failed to add parts');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-500',
      in_progress: 'bg-blue-500',
      scheduled: 'bg-purple-500',
      approved: 'bg-indigo-500',
      pending: 'bg-yellow-500',
    };
    return <Badge className={colors[status] || 'bg-slate-500'}>{status}</Badge>;
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <ModernPageWrapper
      title={workOrder.title}
      subtitle={`WO #${workOrder.wo_number}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/work-orders')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          {workOrder.status === 'pending' && (
            <Button size="sm" onClick={() => handleStatusChange('in_progress')}>
              Start Work
            </Button>
          )}
          {workOrder.status === 'in_progress' && (
            <Button size="sm" onClick={() => handleStatusChange('completed')} className="bg-green-600">
              Complete
            </Button>
          )}
        </div>
      }
    >
      <div className="space-y-6">
        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details"><Wrench className="h-4 w-4 mr-2" />Details</TabsTrigger>
            <TabsTrigger value="labor"><Clock className="h-4 w-4 mr-2" />Labor</TabsTrigger>
            <TabsTrigger value="parts"><Package className="h-4 w-4 mr-2" />Parts</TabsTrigger>
            <TabsTrigger value="timeline"><History className="h-4 w-4 mr-2" />Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader><CardTitle>Work Order Information</CardTitle></CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex justify-between"><span className="font-medium">Status:</span>{getStatusBadge(workOrder.status)}</div>
                  <div className="flex justify-between"><span className="font-medium">Type:</span><Badge variant="outline">{workOrder.work_type}</Badge></div>
                  <div className="flex justify-between"><span className="font-medium">Priority:</span><Badge>{workOrder.priority}</Badge></div>
                  <div><span className="font-medium">Description:</span> {workOrder.description || 'No description'}</div>
                  {workOrder.asset_name && <div><span className="font-medium">Asset:</span> {workOrder.asset_name} ({workOrder.asset_tag})</div>}
                  {workOrder.assigned_to_name && <div><span className="font-medium">Assigned To:</span> {workOrder.assigned_to_name}</div>}
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><DollarSign className="h-5 w-5" />Costs</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between text-sm"><span>Labor Cost:</span><span className="font-bold">${workOrder.labor_cost?.toLocaleString() || '0'}</span></div>
                  <div className="flex justify-between text-sm"><span>Parts Cost:</span><span className="font-bold">${workOrder.parts_cost?.toLocaleString() || '0'}</span></div>
                  <div className="flex justify-between text-lg font-bold border-t pt-2"><span>Total:</span><span>${workOrder.total_cost?.toLocaleString() || '0'}</span></div>
                  {workOrder.estimated_hours && (
                    <div className="flex justify-between text-sm"><span>Estimated Hours:</span><span>{workOrder.estimated_hours}h</span></div>
                  )}
                  {workOrder.actual_hours && (
                    <div className="flex justify-between text-sm"><span>Actual Hours:</span><span className="font-bold">{workOrder.actual_hours}h</span></div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="labor">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Labor Hours</CardTitle>
                  <Button size="sm" onClick={() => setShowTimeDialog(true)}>
                    <Clock className="h-4 w-4 mr-2" />
                    Log Time
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                    <div className="text-sm text-muted-foreground">Total Labor Hours</div>
                    <div className="text-3xl font-bold">{workOrder.actual_hours || 0}h</div>
                    <div className="text-sm text-muted-foreground">Labor Cost: ${workOrder.labor_cost?.toLocaleString() || '0'}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="parts">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Parts Used</CardTitle>
                  <Dialog open={showPartsDialog} onOpenChange={setShowPartsDialog}>
                    <DialogTrigger asChild>
                      <Button size="sm"><Package className="h-4 w-4 mr-2" />Add Parts</Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader><DialogTitle>Add Parts</DialogTitle></DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>Part Name</Label>
                          <Input value={partsData.part_name} onChange={(e) => setPartsData({...partsData, part_name: e.target.value})} />
                        </div>
                        <div className="space-y-2">
                          <Label>Cost</Label>
                          <Input type="number" step="0.01" value={partsData.cost} onChange={(e) => setPartsData({...partsData, cost: e.target.value})} />
                        </div>
                        <Button onClick={handleAddParts} className="w-full">
                          <Save className="h-4 w-4 mr-2" />
                          Save Parts
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-amber-50 dark:bg-amber-950/20 rounded-lg">
                  <div className="text-sm text-muted-foreground">Total Parts Cost</div>
                  <div className="text-3xl font-bold">${workOrder.parts_cost?.toLocaleString() || '0'}</div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="timeline">
            <Card>
              <CardHeader><CardTitle>Activity Timeline</CardTitle></CardHeader>
              <CardContent>
                {timeline.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No activity yet</div>
                ) : (
                  <div className="space-y-3">
                    {timeline.map((entry, idx) => (
                      <div key={idx} className="flex gap-3 p-3 border-l-2 border-primary">
                        <div className="flex-1">
                          <div className="font-medium">{entry.action}</div>
                          <div className="text-sm text-muted-foreground">{entry.created_at?.substring(0, 16)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <TimeLoggingDialog
          taskId={woId}
          open={showTimeDialog}
          onClose={() => setShowTimeDialog(false)}
          onSuccess={() => loadData()}
        />
      </div>
    </ModernPageWrapper>
  );
};

export default WorkOrderDetailPage;
