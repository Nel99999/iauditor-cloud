// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, ListTodo, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TasksPage = () => {
  const [tasks, setTasks] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [formData, setFormData] = useState<any>({ title: '', description: '', priority: 'medium', status: 'todo', due_date: '', tags: [] });
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksRes, statsRes] = await Promise.all([
        axios.get(`${API}/tasks`),
        axios.get(`${API}/tasks/stats/overview`),
      ]);
      setTasks(tasksRes.data);
      setStats(statsRes.data);
    } catch (err: unknown) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: any) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/tasks`, formData);
      setShowCreateDialog(false);
      setFormData({ title: '', description: '', priority: 'medium', status: 'todo', due_date: '', tags: [] });
      loadData();
    } catch (err: unknown) {
      alert('Failed to create task');
    }
  };

  const handleStatusChange = async (taskId, newStatus: any) => {
    try {
      await axios.put(`${API}/tasks/${taskId}`, { status: newStatus });
      loadData();
    } catch (err: unknown) {
      alert('Failed to update task');
    }
  };

  // const _getStatusBadge = (status: any) => {
  //   const badges = {
  //     todo: <Badge variant="secondary">To Do</Badge>,
  //     in_progress: <Badge className="bg-blue-500">In Progress</Badge>,
  //     completed: <Badge className="bg-green-500">Completed</Badge>,
  //     blocked: <Badge variant="destructive">Blocked</Badge>,
  //   };
  //   return badges[status] || <Badge>{status}</Badge>;
  // };

  const getPriorityBadge = (priority: any) => {
    const badges = {
      low: <Badge variant="outline">Low</Badge>,
      medium: <Badge variant="secondary">Medium</Badge>,
      high: <Badge className="bg-orange-500">High</Badge>,
      urgent: <Badge variant="destructive">Urgent</Badge>,
    };
    return badges[priority] || <Badge>{priority}</Badge>;
  };

  const groupByStatus = (tasks: any) => {
    return {
      todo: tasks.filter((t: any) => t.status === 'todo'),
      in_progress: tasks.filter((t: any) => t.status === 'in_progress'),
      completed: tasks.filter((t: any) => t.status === 'completed'),
    };
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  const grouped = groupByStatus(tasks);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Tasks</h1>
          <p className="text-slate-600 dark:text-slate-400">Manage and track tasks</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} data-testid="create-task-btn">
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">To Do</CardTitle>
            <ListTodo className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.todo || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.in_progress || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.completed || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.overdue || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['todo', 'in_progress', 'completed'].map((status) => (
          <Card key={status}>
            <CardHeader>
              <CardTitle className="capitalize">{status.replace('_', ' ')} ({grouped[status].length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {grouped[status].map((task: any) => (
                <Card key={task.id} className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                  <div className="space-y-2">
                    <h4 className="font-semibold">{task.title}</h4>
                    <div className="flex gap-2">
                      {getPriorityBadge(task.priority)}
                      {task.due_date && <Badge variant="outline">{task.due_date}</Badge>}
                    </div>
                    {task.assigned_to_name && <p className="text-sm text-slate-600">Assigned: {task.assigned_to_name}</p>}
                    <Select value={task.status} onValueChange={(val) => handleStatusChange(task.id, val)}>
                      <SelectTrigger className="h-8"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="todo">To Do</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="blocked">Blocked</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </Card>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate}>
            <div className="space-y-4">
              <div>
                <Label>Title *</Label>
                <Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} required data-testid="task-title-input" />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Priority</Label>
                  <Select value={formData.priority} onValueChange={(val) => setFormData({...formData, priority: val})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Due Date</Label>
                  <Input type="date" value={formData.due_date} onChange={(e) => setFormData({...formData, due_date: e.target.value})} />
                </div>
              </div>
            </div>
            <DialogFooter className="mt-4">
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button type="submit" data-testid="save-task-btn">Create Task</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TasksPage;
