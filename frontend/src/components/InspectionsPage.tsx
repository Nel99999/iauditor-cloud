// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { PermissionGuard } from '@/components/PermissionGuard';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import InspectionAnalyticsDashboard from '@/components/InspectionAnalyticsDashboard';
import InspectionCalendar from '@/components/InspectionCalendar';
import {
  ClipboardCheck,
  Plus,
  Play,
  CheckCircle,
  Clock,
  TrendingUp,
  Eye,
  Edit,
  Trash2,
  Copy,
  BarChart3,
  Calendar as CalendarIcon,
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InspectionsPage = () => {
  const navigate = useNavigate();
  // const { user } = useAuth();
  const [templates, setTemplates] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedTemplateForAnalytics, setSelectedTemplateForAnalytics] = useState<any>(null);
  const [showAnalyticsDialog, setShowAnalyticsDialog] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templatesRes, executionsRes, statsRes] = await Promise.all([
        axios.get(`${API}/inspections/templates`),
        axios.get(`${API}/inspections/executions?limit=50`),
        axios.get(`${API}/inspections/stats`),
      ]);

      setTemplates(templatesRes.data);
      setExecutions(executionsRes.data);
      setStats(statsRes.data);
    } catch (err: unknown) {
      console.error('Failed to load inspections:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await axios.delete(`${API}/inspections/templates/${templateId}`);
      loadData();
    } catch (err: unknown) {
      alert('Failed to delete template');
    }
  };

  const handleStartInspection = (templateId: any) => {
    navigate(`/inspections/execute/${templateId}`);
  };

  const formatDate = (dateString: any) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status: any) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500">Completed</Badge>;
      case 'in_progress':
        return <Badge className="bg-yellow-500">In Progress</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <ModernPageWrapper
      title="Inspections"
      subtitle="Manage inspections and audits"
      actions={
        <PermissionGuard
          anyPermissions={['inspection.create.organization', 'inspection.create.own']}
          tooltipMessage="No permission to create inspection templates"
        >
          <Button onClick={() => navigate('/inspections/templates/new')} data-testid="create-template-btn">
            <Plus className="h-4 w-4 mr-2" />
            New Template
          </Button>
        </PermissionGuard>
      }
    >
      <Tabs defaultValue="list" className="space-y-4">
        <TabsList>
          <TabsTrigger value="list">Inspections</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        </TabsList>

        <TabsContent value="list">
          <Card>
            <CardHeader>
              <CardTitle>Recent Inspections</CardTitle>
              <CardDescription>View and manage recent inspection executions</CardDescription>
            </CardHeader>
            <CardContent>
              {executions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No inspections found
                </div>
              ) : (
                <div className="space-y-4">
                  {executions.map((execution) => (
                    <div key={execution.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <div className="font-medium">{execution.template_name || 'Untitled Inspection'}</div>
                        <div className="text-sm text-muted-foreground">
                          {formatDate(execution.created_at)} • {execution.performed_by_name || 'Unknown User'}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={execution.passed ? 'default' : 'destructive'}>
                          {execution.passed ? 'Passed' : 'Failed'}
                        </Badge>
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/inspections/executions/${execution.id}`)}>
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          {templates.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12 text-muted-foreground">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">No templates available</h3>
                  <p className="text-sm">Create inspection templates to view analytics</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Select Template for Analytics</CardTitle>
                  <CardDescription>Choose a template to view detailed performance metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <Select
                    value={selectedTemplateForAnalytics?.id || ''}
                    onValueChange={(value) => {
                      const template = templates.find(t => t.id === value);
                      setSelectedTemplateForAnalytics(template);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a template..." />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.map(template => (
                        <SelectItem key={template.id} value={template.id}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {selectedTemplateForAnalytics && (
                <InspectionAnalyticsDashboard
                  templateId={selectedTemplateForAnalytics.id}
                  templateName={selectedTemplateForAnalytics.name}
                />
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="calendar">
          <InspectionCalendar />
        </TabsContent>
      </Tabs>

      <Dialog open={showAnalyticsDialog} onOpenChange={setShowAnalyticsDialog}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Template Analytics</DialogTitle>
          </DialogHeader>
          {selectedTemplateForAnalytics && (
            <InspectionAnalyticsDashboard
              templateId={selectedTemplateForAnalytics.id}
              templateName={selectedTemplateForAnalytics.name}
            />
          )}
        </DialogContent>
      </Dialog>
    </ModernPageWrapper>
  );
};

export default InspectionsPage;