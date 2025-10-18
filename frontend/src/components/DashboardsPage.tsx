// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, Shield, Wrench, TrendingUp, Package, 
  ClipboardCheck, ListTodo, FolderKanban, AlertTriangle 
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardsPage = () => {
  const [executive, setExecutive] = useState(null);
  const [safety, setSafety] = useState(null);
  const [maintenance, setMaintenance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAllDashboards();
  }, []);

  const loadAllDashboards = async () => {
    try {
      const [execRes, safetyRes, maintRes] = await Promise.all([
        axios.get(`${API}/dashboards/executive`),
        axios.get(`${API}/dashboards/safety`),
        axios.get(`${API}/dashboards/maintenance`),
      ]);
      setExecutive(execRes.data);
      setSafety(safetyRes.data);
      setMaintenance(maintRes.data);
    } catch (err) {
      console.error('Failed to load dashboards:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <ModernPageWrapper title="Enterprise Dashboards" subtitle="Key performance indicators">
      <Tabs defaultValue="executive" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="executive"><TrendingUp className="h-4 w-4 mr-2" />Executive</TabsTrigger>
          <TabsTrigger value="safety"><Shield className="h-4 w-4 mr-2" />Safety</TabsTrigger>
          <TabsTrigger value="maintenance"><Wrench className="h-4 w-4 mr-2" />Maintenance</TabsTrigger>
        </TabsList>

        <TabsContent value="executive">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><ListTodo className="h-4 w-4" />Tasks</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{executive?.overview?.total_tasks || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Package className="h-4 w-4" />Assets</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{executive?.overview?.total_assets || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Wrench className="h-4 w-4" />Work Orders</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{executive?.overview?.total_work_orders || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><AlertTriangle className="h-4 w-4" />Incidents</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{executive?.overview?.total_incidents || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><FolderKanban className="h-4 w-4" />Projects</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{executive?.overview?.total_projects || 0}</div></CardContent>
            </Card>
          </div>
          <Card className="mt-6">
            <CardHeader><CardTitle>Recent Activity (Last 7 Days)</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded">
                <span className="flex items-center gap-2"><ClipboardCheck className="h-4 w-4" />Inspections Completed</span>
                <span className="font-bold">{executive?.recent_activity?.inspections_last_7_days || 0}</span>
              </div>
              <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-900 rounded">
                <span className="flex items-center gap-2"><ClipboardCheck className="h-4 w-4" />Checklists Completed</span>
                <span className="font-bold">{executive?.recent_activity?.checklists_last_7_days || 0}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="safety">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Total Incidents</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{safety?.total_incidents || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">This Month</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{safety?.this_month || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm text-red-600">Injuries</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold text-red-600">{safety?.injuries || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm text-green-600">Near Misses</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold text-green-600">{safety?.near_misses || 0}</div></CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="maintenance">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm text-amber-600">Backlog</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold text-amber-600">{maintenance?.work_order_backlog || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm text-blue-600">In Progress</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold text-blue-600">{maintenance?.in_progress || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm text-green-600">Completed</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold text-green-600">{maintenance?.completed || 0}</div></CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">PM Compliance</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-bold">{maintenance?.pm_compliance_percentage || 0}%</div></CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </ModernPageWrapper>
  );
};

export default DashboardsPage;
