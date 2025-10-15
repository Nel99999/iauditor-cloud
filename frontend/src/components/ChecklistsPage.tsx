import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Plus, CheckCircle, Clock, AlertTriangle, TrendingUp, Play, Edit, Trash2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChecklistsPage : React.FC = () => {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [todaysChecklists, setTodaysChecklists] = useState({ executions: [], pending_templates: [] });
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templatesRes, todayRes, statsRes] = await Promise.all([
        axios.get(`${API}/checklists/templates`),
        axios.get(`${API}/checklists/executions/today`),
        axios.get(`${API}/checklists/stats`),
      ]);
      
      setTemplates(templatesRes.data);
      setTodaysChecklists(todayRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load checklists:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartChecklist = async (templateId) => {
    try {
      await axios.post(`${API}/checklists/executions?template_id=${templateId}`);
      loadData();
    } catch (err) {
      console.error('Failed to start checklist:', err);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Delete this template?')) return;
    try {
      await axios.delete(`${API}/checklists/templates/${templateId}`);
      loadData();
    } catch (err) {
      alert('Failed to delete template');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500">Completed</Badge>;
      case 'in_progress':
        return <Badge className="bg-yellow-500">In Progress</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
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
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Checklists</h1>
          <p className="text-slate-600 dark:text-slate-400">Daily operational checklists</p>
        </div>
        <Button onClick={() => navigate('/checklists/templates/new')} data-testid="create-checklist-template-btn">
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Today</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_today || 0}</div>
            <p className="text-xs text-muted-foreground">Need completion</p>
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
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.completion_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">Overall</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.overdue || 0}</div>
            <p className="text-xs text-muted-foreground">Needs attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="today" className="space-y-6">
        <TabsList>
          <TabsTrigger value="today">Today ({(todaysChecklists.executions?.length || 0) + (todaysChecklists.pending_templates?.length || 0)})</TabsTrigger>
          <TabsTrigger value="templates">Templates ({templates.length})</TabsTrigger>
        </TabsList>

        {/* Today's Checklists */}
        <TabsContent value="today">
          <div className="space-y-4">
            {/* Pending checklists to start */}
            {todaysChecklists.pending_templates?.map((template) => (
              <Card key={template.id} className="border-2 border-dashed">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold">{template.name}</h3>
                      {template.category && <Badge variant="outline" className="mt-1 capitalize">{template.category}</Badge>}
                    </div>
                    <Button onClick={() => handleStartChecklist(template.id)} size="sm">
                      <Play className="h-4 w-4 mr-1" />
                      Start
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Active checklists */}
            {todaysChecklists.executions?.map((execution) => (
              <Card
                key={execution.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => navigate(`/checklists/execute/${execution.id}`)}
              >
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{execution.template_name}</h3>
                          {getStatusBadge(execution.status)}
                        </div>
                        {execution.completed_by_name && (
                          <p className="text-sm text-slate-600 mt-1">
                            By: {execution.completed_by_name}
                          </p>
                        )}
                      </div>
                      <div className="text-2xl font-bold">{execution.completion_percentage}%</div>
                    </div>
                    <Progress value={execution.completion_percentage} />
                  </div>
                </CardContent>
              </Card>
            ))}

            {todaysChecklists.executions?.length === 0 && todaysChecklists.pending_templates?.length === 0 && (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <CheckCircle className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                    <h3 className="text-lg font-semibold mb-2">No checklists for today</h3>
                    <p className="text-slate-600 mb-4">Create a template to get started</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          {templates.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-semibold mb-2">No templates yet</h3>
                  <p className="text-slate-600 mb-4">Create your first checklist template</p>
                  <Button onClick={() => navigate('/checklists/templates/new')}>
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
                        <Badge variant="outline" className="capitalize">{template.category}</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2 text-sm text-slate-600">
                      <span className="font-medium">{template.items.length}</span> items
                      <span>•</span>
                      <span className="capitalize">{template.frequency}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        className="flex-1"
                        onClick={() => handleStartChecklist(template.id)}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Start
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigate(`/checklists/templates/${template.id}/edit`)}
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
      </Tabs>
    </div>
  );
};

export default ChecklistsPage;
