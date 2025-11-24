// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { PermissionGuard } from '@/components/PermissionGuard';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, ListTodo, Clock, CheckCircle, AlertTriangle, User, Users, MessageSquare, Send } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TasksPage = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [formData, setFormData] = useState<any>({ title: '', description: '', priority: 'medium', status: 'todo', due_date: '', tags: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [filter, setFilter] = useState<'all' | 'my'>('my'); // Default to 'my' tasks

  // Task Details & Comments
  const [selectedTask, setSelectedTask] = useState<any | null>(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState<boolean>(false);
  const [newComment, setNewComment] = useState<string>('');
  const [commenting, setCommenting] = useState<boolean>(false);

  useEffect(() => {
    loadData();
  }, [filter]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Build query params
      const params = new URLSearchParams();
      if (filter === 'my' && user) {
        params.append('assigned_to', user.id);
      }

      const [tasksRes, statsRes] = await Promise.all([
        axios.get(`${API}/tasks?${params.toString()}`),
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

  const handleStatusChange = async (taskId: string, newStatus: any, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent opening details
    try {
      await axios.put(`${API}/tasks/${taskId}`, { status: newStatus });
      loadData();
      if (selectedTask && selectedTask.id === taskId) {
        // Update selected task if open
        setSelectedTask(prev => ({ ...prev, status: newStatus }));
      }
    } catch (err: unknown) {
      alert('Failed to update task');
    }
  };

  const handleTaskClick = (task: any) => {
    setSelectedTask(task);
    setShowDetailsDialog(true);
  };

  const handlePostComment = async () => {
    if (!newComment.trim()) return;

    try {
      setCommenting(true);
      const res = await axios.post(`${API}/tasks/${selectedTask.id}/comments`, {
        text: newComment
      });

      // Update local state
      const updatedComments = [...(selectedTask.comments || []), res.data.comment];
      setSelectedTask({ ...selectedTask, comments: updatedComments });

      // Update tasks list
      setTasks(tasks.map(t => t.id === selectedTask.id ? { ...t, comments: updatedComments } : t));

      setNewComment('');
    } catch (err) {
      console.error("Failed to post comment", err);
      alert("Failed to post comment");
    } finally {
      setCommenting(false);
    }
  };

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

  if (loading && !tasks.length) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  const grouped = groupByStatus(tasks);

  return (
    <ModernPageWrapper
      title="Tasks"
      subtitle="Manage and track your tasks"
      actions={
        <div className="flex gap-2">
          <div className="bg-slate-100 dark:bg-slate-800 p-1 rounded-lg flex">
            <Button
              variant={filter === 'my' ? 'white' : 'ghost'}
              size="sm"
              onClick={() => setFilter('my')}
              className={filter === 'my' ? 'shadow-sm' : ''}
            >
              <User className="h-4 w-4 mr-2" />
              My Tasks
            </Button>
            <Button
              variant={filter === 'all' ? 'white' : 'ghost'}
              size="sm"
              onClick={() => setFilter('all')}
              className={filter === 'all' ? 'shadow-sm' : ''}
            >
              <Users className="h-4 w-4 mr-2" />
              All Tasks
            </Button>
          </div>
          <PermissionGuard
            anyPermissions={['task.create.organization', 'task.create.own']}
            tooltipMessage="No permission to create tasks"
          >
            <Button onClick={() => setShowCreateDialog(true)} data-testid="create-task-btn">
              <Plus className="h-4 w-4 mr-2" />
              New Task
            </Button>
          </PermissionGuard>
        </div>
      }
    >
      <div className="space-y-6">

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
            <Card key={status} className="bg-slate-50 dark:bg-slate-900/50 border-none">
              <CardHeader className="pb-3">
                <CardTitle className="capitalize flex justify-between items-center text-base">
                  {status.replace('_', ' ')}
                  <Badge variant="outline" className="ml-2">{grouped[status].length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 min-h-[200px]">
                {grouped[status].map((task: any) => (
                  <Card
                    key={task.id}
                    className="p-4 cursor-pointer hover:shadow-md transition-all hover:border-primary/50 group bg-white dark:bg-slate-800"
                    onClick={() => handleTaskClick(task)}
                  >
                    <div className="space-y-3">
                      <div className="flex justify-between items-start gap-2">
                        <h4 className="font-semibold text-sm line-clamp-2 group-hover:text-primary transition-colors">{task.title}</h4>
                        {getPriorityBadge(task.priority)}
                      </div>

                      <div className="flex justify-between items-center text-xs text-muted-foreground">
                        {task.due_date && (
                          <span className={`flex items-center ${new Date(task.due_date) < new Date() && task.status !== 'completed' ? 'text-red-500 font-medium' : ''}`}>
                            <Clock className="h-3 w-3 mr-1" />
                            {task.due_date}
                          </span>
                        )}
                        {task.comments?.length > 0 && (
                          <span className="flex items-center">
                            <MessageSquare className="h-3 w-3 mr-1" />
                            {task.comments.length}
                          </span>
                        )}
                      </div>

                      {task.assigned_to_name && (
                        <div className="flex items-center text-xs text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/50 p-1.5 rounded">
                          <User className="h-3 w-3 mr-1.5" />
                          {task.assigned_to_name}
                        </div>
                      )}

                      <div onClick={(e) => e.stopPropagation()}>
                        <Select value={task.status} onValueChange={(val) => handleStatusChange(task.id, val, {} as any)}>
                          <SelectTrigger className="h-7 text-xs w-full"><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="todo">To Do</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="completed">Completed</SelectItem>
                            <SelectItem value="blocked">Blocked</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </Card>
                ))}
                {grouped[status].length === 0 && (
                  <div className="text-center py-8 text-muted-foreground text-sm border-2 border-dashed rounded-lg">
                    No tasks
                  </div>
                )}
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
                  <Input value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} required data-testid="task-title-input" />
                </div>
                <div>
                  <Label>Description</Label>
                  <Textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Priority</Label>
                    <Select value={formData.priority} onValueChange={(val) => setFormData({ ...formData, priority: val })}>
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
                    <Input type="date" value={formData.due_date} onChange={(e) => setFormData({ ...formData, due_date: e.target.value })} />
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

        {/* Task Details Dialog */}
        <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
          <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex justify-between items-center pr-8">
                <span>{selectedTask?.title}</span>
                {selectedTask && getPriorityBadge(selectedTask.priority)}
              </DialogTitle>
            </DialogHeader>

            <div className="flex-1 overflow-hidden flex flex-col gap-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="mt-1 capitalize font-medium">{selectedTask?.status?.replace('_', ' ')}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Due Date</Label>
                  <div className="mt-1 font-medium">{selectedTask?.due_date || 'No due date'}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Assigned To</Label>
                  <div className="mt-1 font-medium">{selectedTask?.assigned_to_name || 'Unassigned'}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Created By</Label>
                  <div className="mt-1 font-medium">{selectedTask?.created_by_name}</div>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                <Label className="text-muted-foreground mb-2 block">Description</Label>
                <p className="text-sm whitespace-pre-wrap">{selectedTask?.description || 'No description provided.'}</p>
              </div>

              <div className="flex-1 flex flex-col min-h-0">
                <Label className="mb-2 flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Comments ({selectedTask?.comments?.length || 0})
                </Label>

                <ScrollArea className="flex-1 border rounded-md p-4 mb-4">
                  {selectedTask?.comments?.length > 0 ? (
                    <div className="space-y-4">
                      {selectedTask.comments.map((comment: any, idx: number) => (
                        <div key={idx} className="flex gap-3">
                          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                            {comment.user?.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between items-baseline">
                              <span className="font-semibold text-sm">{comment.user}</span>
                              <span className="text-xs text-muted-foreground">
                                {new Date(comment.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-sm mt-1 text-slate-700 dark:text-slate-300">{comment.text}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground text-sm py-8">
                      No comments yet. Be the first to comment!
                    </div>
                  )}
                </ScrollArea>

                <div className="flex gap-2">
                  <Textarea
                    placeholder="Write a comment..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="min-h-[60px]"
                  />
                  <Button
                    size="icon"
                    className="h-[60px] w-[60px]"
                    onClick={handlePostComment}
                    disabled={!newComment.trim() || commenting}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>

      </div>
    </ModernPageWrapper>
  );
};

export default TasksPage;
