import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InspectionsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [templates, setTemplates] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Inspections
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage inspection templates and executions
          </p>
        </div>
        <Button onClick={() => navigate('/inspections/templates/new')} data-testid="create-template-btn">
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending || 0}</div>
            <p className="text-xs text-muted-foreground">In progress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.completed_today || 0}</div>
            <p className="text-xs text-muted-foreground">Today's count</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pass_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">Success rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.average_score ? `${stats.average_score}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">Average</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="templates" className="space-y-6">
        <TabsList>
          <TabsTrigger value="templates">Templates ({templates.length})</TabsTrigger>
          <TabsTrigger value="executions">Executions ({executions.length})</TabsTrigger>
        </TabsList>

        {/* Templates Tab */}
        <TabsContent value="templates">
          {templates.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <ClipboardCheck className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-semibold mb-2">No templates yet</h3>
                  <p className="text-slate-600 mb-4">Create your first inspection template to get started</p>
                  <Button onClick={() => navigate('/inspections/templates/new')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {templates.map((template) => (
                <Card key={template.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{template.name}</CardTitle>
                        <CardDescription className="mt-1">
                          {template.description || 'No description'}
                        </CardDescription>
                      </div>
                      {template.category && (
                        <Badge variant="outline" className="capitalize">
                          {template.category}
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2 text-sm text-slate-600">
                      <div>
                        <span className="font-medium">{template.questions.length}</span> questions
                      </div>
                      {template.scoring_enabled && (
                        <>
                          <span>•</span>
                          <div>
                            Pass: <span className="font-medium">{template.pass_percentage}%</span>
                          </div>
                        </>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        className="flex-1"
                        onClick={() => handleStartInspection(template.id)}
                        data-testid={`start-inspection-${template.id}`}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Start
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigate(`/inspections/templates/${template.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigate(`/inspections/templates/${template.id}/edit`)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteTemplate(template.id)}
                        className="text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Executions Tab */}
        <TabsContent value="executions">
          {executions.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <ClipboardCheck className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-semibold mb-2">No inspections yet</h3>
                  <p className="text-slate-600 mb-4">Start an inspection from a template</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {executions.map((execution: any) => (
                    <div
                      key={execution.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                      onClick={() => navigate(`/inspections/executions/${execution.id}`)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{execution.template_name}</h4>
                          {getStatusBadge(execution.status)}
                        </div>
                        <div className="text-sm text-slate-600 mt-1">
                          Inspector: {execution.inspector_name} • {formatDate(execution.started_at)}
                        </div>
                      </div>
                      <div className="text-right">
                        {execution.score !== null && (
                          <div className="text-lg font-bold">{execution.score}%</div>
                        )}
                        {execution.passed !== null && (
                          <Badge
                            variant={execution.passed ? 'default' : 'destructive'}
                            className="mt-1"
                          >
                            {execution.passed ? 'Passed' : 'Failed'}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default InspectionsPage;