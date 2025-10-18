// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Wrench, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkOrdersPage = () => {
  const navigate = useNavigate();
  const [workOrders, setWorkOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [wosRes, statsRes] = await Promise.all([
        axios.get(`${API}/work-orders`),
        axios.get(`${API}/work-orders/stats/overview`),
      ]);
      setWorkOrders(wosRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load work orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-500',
      in_progress: 'bg-blue-500',
      scheduled: 'bg-purple-500',
      approved: 'bg-indigo-500',
      pending: 'bg-yellow-500',
      cancelled: 'bg-red-500',
    };
    return <Badge className={colors[status] || 'bg-slate-500'}>{status}</Badge>;
  };

  return (
    <ModernPageWrapper 
      title="Work Orders" 
      subtitle="CMMS - Maintenance work orders"
      actions={
        <Button onClick={() => navigate('/work-orders/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Work Order
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Work Orders</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_work_orders || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Backlog</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold text-amber-600">{stats?.backlog_count || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Completed (Month)</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.completed_this_month || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Avg Hours</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.average_completion_hours ? `${stats.average_completion_hours}h` : 'N/A'}</div></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Work Orders ({workOrders.length})</CardTitle></CardHeader>
          <CardContent>
            {workOrders.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No work orders yet</div>
            ) : (
              <div className="space-y-3">
                {workOrders.map((wo) => (
                  <div 
                    key={wo.id} 
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900 cursor-pointer transition-colors"
                    onClick={() => navigate(`/work-orders/${wo.id}`)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{wo.title}</span>
                        {getStatusBadge(wo.status)}
                        <Badge variant="outline">{wo.work_type}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {wo.wo_number} • {wo.asset_name || 'No asset'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default WorkOrdersPage;
