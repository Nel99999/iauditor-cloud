// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Circle, ChevronDown, ChevronRight, Plus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubtaskTreeView = ({ taskId, onAddSubtask }) => {
  const [subtasks, setSubtasks] = useState([]);
  const [expanded, setExpanded] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubtasks();
  }, [taskId]);

  const loadSubtasks = async () => {
    try {
      const response = await axios.get(`${API}/tasks/${taskId}/subtasks`);
      setSubtasks(response.data);
    } catch (err) {
      console.error('Failed to load subtasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    return status === 'completed' ? (
      <CheckCircle className="h-4 w-4 text-green-600" />
    ) : (
      <Circle className="h-4 w-4 text-slate-400" />
    );
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-500',
      in_progress: 'bg-blue-500',
      todo: 'bg-slate-500',
      blocked: 'bg-red-500',
    };
    return <Badge className={colors[status] || 'bg-slate-500'}>{status}</Badge>;
  };

  if (loading) {
    return <div className="text-sm text-muted-foreground">Loading subtasks...</div>;
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-2">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </Button>
              <h4 className="font-semibold">Subtasks ({subtasks.length})</h4>
            </div>
            <Button size="sm" variant="outline" onClick={onAddSubtask}>
              <Plus className="h-4 w-4 mr-2" />
              Add Subtask
            </Button>
          </div>

          {expanded && (
            subtasks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No subtasks yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {subtasks.map((subtask) => (
                  <div
                    key={subtask.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(subtask.status)}
                      <div className="flex-1">
                        <div className="font-medium">{subtask.title}</div>
                        {subtask.assigned_to_name && (
                          <div className="text-sm text-muted-foreground">
                            Assigned to: {subtask.assigned_to_name}
                          </div>
                        )}
                      </div>
                    </div>
                    {getStatusBadge(subtask.status)}
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default SubtaskTreeView;
