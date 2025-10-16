import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { GlassCard, Button, Input, ModernPageWrapper, Spinner, BottomSheet, useBottomSheet, FAB, FABIcons } from '@/design-system/components';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Clock, CheckCircle, AlertTriangle, Edit, Trash2, LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import './TasksPageNew.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Types
interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'todo' | 'in-progress' | 'done';
  due_date?: string;
  created_at?: string;
  tags?: string[];
  [key: string]: any;
}

interface TaskStats {
  total?: number;
  in_progress?: number;
  completed?: number;
}

interface FormData {
  title: string;
  description: string;
  priority: string;
  status: string;
  due_date: string;
  tags: string[];
}

interface StatCard {
  label: string;
  value: number;
  icon: LucideIcon;
  color: string;
}

const TasksPageNew = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [formData, setFormData] = useState<FormData>({ title: '', description: '', priority: 'medium', status: 'todo', due_date: '', tags: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  
  // BottomSheet for task details
  const { isOpen: isDetailsOpen, open: openDetails, close: closeDetails } = useBottomSheet(false, 'half');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const [tasksRes, statsRes] = await Promise.all([
        axios.get<Task[]>(`${API}/tasks`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get<TaskStats>(`${API}/tasks/stats/overview`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      setTasks(tasksRes.data || []);
      setStats(statsRes.data || {});
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/tasks`, formData, { headers: { Authorization: `Bearer ${token}` } });
      setShowCreateDialog(false);
      setFormData({ title: '', description: '', priority: 'medium', status: 'todo', due_date: '', tags: [] });
      loadData();
    } catch (err) {
      alert('Failed to create task');
    }
  };

  const priorityColors: Record<string, string> = {
    low: 'bg-blue-500',
    medium: 'bg-yellow-500',
    high: 'bg-orange-500',
    urgent: 'bg-red-500',
  };

  const statusIcons: Record<string, LucideIcon> = {
    todo: Clock,
    'in-progress': AlertTriangle,
    done: CheckCircle,
  };

  if (loading) {
    return (
      <ModernPageWrapper title="Tasks">
        <div className="tasks-loading">
          <Spinner size="xl" />
          <p>Loading tasks...</p>
        </div>
      </ModernPageWrapper>
    );
  }

  return (
    <ModernPageWrapper
      title="Tasks"
      subtitle="Manage and track your tasks"
      actions={
        <Button variant="primary" size="md" icon={<Plus size={20} />} onClick={() => setShowCreateDialog(true)}>
          Create Task
        </Button>
      }
    >
      {/* Stats Cards */}
      <div className="tasks-stats-grid">
        {([
          { label: 'Total Tasks', value: stats?.total || 0, icon: Clock, color: 'blue' },
          { label: 'In Progress', value: stats?.in_progress || 0, icon: AlertTriangle, color: 'orange' },
          { label: 'Completed', value: stats?.completed || 0, icon: CheckCircle, color: 'green' },
        ] as StatCard[]).map((stat: any, index: number) => {
          const Icon = stat.icon;
          return (
            <motion.div key={index} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}>
              <GlassCard hover className="stat-card-tasks">
                <div className="stat-icon-wrapper">
                  <Icon size={24} />
                </div>
                <div className="stat-content">
                  <p className="stat-label">{stat.label}</p>
                  <h3 className="stat-value">{stat.value}</h3>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>

      {/* Tasks List */}
      <GlassCard padding="lg" className="tasks-list-card">
        <h2 className="tasks-list-title">All Tasks</h2>
        {tasks.length === 0 ? (
          <div className="tasks-empty">
            <p>No tasks yet. Create your first task!</p>
          </div>
        ) : (
          <div className="tasks-list">
            {tasks.map((task: any, index: number) => {
              const StatusIcon = statusIcons[task.status] || Clock;
              return (
                <motion.div
                  key={task.id}
                  className="task-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="task-icon">
                    <StatusIcon size={20} />
                  </div>
                  <div className="task-content" onClick={() => { setSelectedTask(task); openDetails(); }} style={{ cursor: 'pointer' }}>
                    <h4 className="task-title">{task.title}</h4>
                    <p className="task-description">{task.description}</p>
                    <div className="task-meta">
                      <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
                      <span className="task-status">{task.status}</span>
                      {task.due_date && <span className="task-due">Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div className="task-actions">
                    <Button variant="ghost" size="sm" icon={<Edit size={16} />} onClick={() => { setSelectedTask(task); setShowCreateDialog(true); }} />
                    <Button variant="ghost" size="sm" icon={<Trash2 size={16} />} />
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </GlassCard>

      {/* Create Task Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="modern-dialog">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreate} className="task-form">
            <div className="form-group">
              <Label>Title</Label>
              <Input value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} required size="lg" />
            </div>
            <div className="form-group">
              <Label>Description</Label>
              <Textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
            </div>
            <div className="form-group">
              <Label>Priority</Label>
              <Select value={formData.priority} onValueChange={(value) => setFormData({ ...formData, priority: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="button" variant="secondary" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Create Task
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Task Details Bottom Sheet */}
      <BottomSheet
        isOpen={isDetailsOpen}
        onClose={() => { closeDetails(); setSelectedTask(null); }}
        snapPoint="half"
        title="Task Details"
      >
        {selectedTask && (
          <div className="task-details-content">
            <div className="task-detail-section">
              <h3 className="task-detail-title">{selectedTask.title}</h3>
              <div className="task-detail-meta">
                <Badge className={priorityColors[selectedTask.priority]}>{selectedTask.priority}</Badge>
                <span className="task-detail-status">{selectedTask.status}</span>
              </div>
            </div>
            
            <div className="task-detail-section">
              <h4 className="task-detail-label">Description</h4>
              <p className="task-detail-text">{selectedTask.description || 'No description provided'}</p>
            </div>

            {selectedTask.due_date && (
              <div className="task-detail-section">
                <h4 className="task-detail-label">Due Date</h4>
                <p className="task-detail-text">{new Date(selectedTask.due_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
              </div>
            )}

            <div className="task-detail-section">
              <h4 className="task-detail-label">Created</h4>
              <p className="task-detail-text">{selectedTask.created_at ? new Date(selectedTask.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'Unknown'}</p>
            </div>

            <div className="task-detail-actions">
              <Button variant="primary" size="md" icon={<Edit size={18} />} onClick={() => { closeDetails(); setShowCreateDialog(true); }}>
                Edit Task
              </Button>
              <Button variant="ghost" size="md" icon={<Trash2 size={18} />}>
                Delete Task
              </Button>
            </div>
          </div>
        )}
      </BottomSheet>

      {/* Floating Action Button */}
      <FAB
        variant="simple"
        position="bottom-right"
        icon={<FABIcons.Plus />}
        label="Create New Task"
        color="primary"
        onClick={() => setShowCreateDialog(true)}
      />
    </ModernPageWrapper>
  );
};

export default TasksPageNew;
