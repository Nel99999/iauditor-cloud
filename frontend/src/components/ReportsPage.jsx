import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ClipboardCheck, 
  CheckSquare, 
  ListTodo, 
  TrendingUp, 
  BarChart3, 
  Download, 
  Plus, 
  Settings,
  AlertTriangle,
  Target,
  Clock,
  FileText
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportsPage = () => {
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, trendsRes] = await Promise.all([
        axios.get(`${API}/reports/overview?days=30`),
        axios.get(`${API}/reports/trends?days=30`),
      ]);
      setOverview(overviewRes.data);
      setTrends(trendsRes.data);
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Reports & Analytics</h1>
        <p className="text-slate-600 dark:text-slate-400">Performance insights and trends (Last {overview?.period_days} days)</p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="inspections">Inspections</TabsTrigger>
          <TabsTrigger value="checklists">Checklists</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Inspections Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Inspections</CardTitle>
                  <ClipboardCheck className="h-5 w-5 text-blue-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.inspections?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Inspections</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.inspections?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pending:</span>
                    <Badge variant="secondary">{overview?.inspections?.pending || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pass Rate:</span>
                    <Badge className="bg-blue-500">{overview?.inspections?.pass_rate || 0}%</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Avg Score:</span>
                    <Badge variant="outline">{overview?.inspections?.avg_score || 0}%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Checklists Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Checklists</CardTitle>
                  <CheckSquare className="h-5 w-5 text-green-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.checklists?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Checklists</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.checklists?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pending:</span>
                    <Badge variant="secondary">{overview?.checklists?.pending || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Completion Rate:</span>
                    <Badge className="bg-blue-500">{overview?.checklists?.completion_rate || 0}%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tasks Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Tasks</CardTitle>
                  <ListTodo className="h-5 w-5 text-purple-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.tasks?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Tasks</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.tasks?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">In Progress:</span>
                    <Badge className="bg-blue-500">{overview?.tasks?.in_progress || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">To Do:</span>
                    <Badge variant="secondary">{overview?.tasks?.todo || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Overdue:</span>
                    <Badge variant="destructive">{overview?.tasks?.overdue || 0}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Trends Preview */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Activity Trends</CardTitle>
              <CardDescription>Daily completions over the last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Inspections Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.inspections || {}).length} days with activity
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Checklists Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.checklists || {}).length} days with activity
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Tasks Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.tasks || {}).length} days with activity
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Detailed Tabs */}
        <TabsContent value="inspections">
          <Card>
            <CardHeader>
              <CardTitle>Inspection Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.inspections?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.inspections?.pass_rate || 0}%</p>
                  <p className="text-sm text-slate-600">Pass Rate</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.inspections?.avg_score || 0}%</p>
                  <p className="text-sm text-slate-600">Avg Score</p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{overview?.inspections?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="checklists">
          <Card>
            <CardHeader>
              <CardTitle>Checklist Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.checklists?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.checklists?.completion_rate || 0}%</p>
                  <p className="text-sm text-slate-600">Completion Rate</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.checklists?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks">
          <Card>
            <CardHeader>
              <CardTitle>Task Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.tasks?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.tasks?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.tasks?.in_progress || 0}</p>
                  <p className="text-sm text-slate-600">In Progress</p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{overview?.tasks?.overdue || 0}</p>
                  <p className="text-sm text-slate-600">Overdue</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReportsPage;
