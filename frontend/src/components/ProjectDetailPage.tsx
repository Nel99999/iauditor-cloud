// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, Target, DollarSign, ListTodo, Calendar, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectDetailPage = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    try {
      const [projectRes, milestonesRes, tasksRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/projects/${projectId}/milestones`),
        axios.get(`${API}/projects/${projectId}/tasks`),
      ]);
      setProject(projectRes.data);
      setMilestones(milestonesRes.data);
      setTasks(tasksRes.data);
    } catch (err) {
      console.error('Failed to load project:', err);
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  const getStatusBadge = (status) => {
    const colors = { completed: 'bg-green-500', active: 'bg-blue-500', planning: 'bg-purple-500', on_hold: 'bg-yellow-500' };
    return <Badge className={colors[status] || 'bg-slate-500'}>{status}</Badge>;
  };

  return (
    <ModernPageWrapper
      title={project.name}
      subtitle={`Project Code: ${project.project_code}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/projects')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Status</CardTitle></CardHeader>
            <CardContent>{getStatusBadge(project.status)}</CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Progress</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{project.completion_percentage}%</div>
              <Progress value={project.completion_percentage} className="mt-2" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Budget</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${project.budget.toLocaleString()}</div>
              <div className="text-xs text-muted-foreground">Spent: ${project.actual_cost.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Tasks</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{project.completed_tasks}/{project.task_count}</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview"><Target className="h-4 w-4 mr-2" />Overview</TabsTrigger>
            <TabsTrigger value="milestones"><Calendar className="h-4 w-4 mr-2" />Milestones</TabsTrigger>
            <TabsTrigger value="tasks"><ListTodo className="h-4 w-4 mr-2" />Tasks</TabsTrigger>
            <TabsTrigger value="budget"><DollarSign className="h-4 w-4 mr-2" />Budget</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <Card>
              <CardHeader><CardTitle>Project Overview</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div><span className="font-medium">Description:</span> {project.description || 'No description'}</div>
                <div><span className="font-medium">Project Manager:</span> {project.project_manager_name}</div>
                <div><span className="font-medium">Type:</span> <Badge variant="outline">{project.project_type}</Badge></div>
                {project.planned_start && <div><span className="font-medium">Planned Start:</span> {project.planned_start}</div>}
                {project.planned_end && <div><span className="font-medium">Planned End:</span> {project.planned_end}</div>}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="milestones">
            <Card>
              <CardHeader><CardTitle>Milestones ({milestones.length})</CardTitle></CardHeader>
              <CardContent>
                {milestones.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No milestones yet</div>
                ) : (
                  <div className="space-y-3">
                    {milestones.map((milestone) => (
                      <div key={milestone.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{milestone.name}</div>
                          <div className="text-sm text-muted-foreground">Due: {milestone.due_date}</div>
                        </div>
                        <Badge>{milestone.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="tasks">
            <Card>
              <CardHeader><CardTitle>Project Tasks ({tasks.length})</CardTitle></CardHeader>
              <CardContent>
                {tasks.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No tasks yet</div>
                ) : (
                  <div className="space-y-2">
                    {tasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{task.title}</div>
                          {task.assigned_to_name && <div className="text-sm text-muted-foreground">Assigned: {task.assigned_to_name}</div>}
                        </div>
                        <Badge>{task.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="budget">
            <Card>
              <CardHeader><CardTitle>Budget Tracking</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Planned Budget</div>
                      <div className="text-2xl font-bold">${project.budget.toLocaleString()}</div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Actual Cost</div>
                      <div className="text-2xl font-bold">${project.actual_cost.toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
                    <div className="text-sm text-muted-foreground">Variance</div>
                    <div className={`text-2xl font-bold ${(project.budget - project.actual_cost) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${(project.budget - project.actual_cost).toLocaleString()}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <TimeLoggingDialog
        taskId={woId}
        open={showTimeDialog}
        onClose={() => setShowTimeDialog(false)}
        onSuccess={() => loadData()}
      />
    </ModernPageWrapper>
  );
};

export default ProjectDetailPage;
