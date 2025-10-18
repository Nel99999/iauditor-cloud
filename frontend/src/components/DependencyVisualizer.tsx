// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GitBranch, ArrowRight } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DependencyVisualizer = ({ taskId }) => {
  const [dependencies, setDependencies] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDependencies();
  }, [taskId]);

  const loadDependencies = async () => {
    try {
      const response = await axios.get(`${API}/tasks/${taskId}/dependencies`);
      setDependencies(response.data);
    } catch (err) {
      console.error('Failed to load dependencies:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !dependencies) {
    return null;
  }

  const { predecessors, subtasks, parent } = dependencies;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-5 w-5" />
          Task Dependencies
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {parent && (
          <div>
            <div className="text-sm font-semibold mb-2">Parent Task</div>
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="font-medium">{parent.title}</div>
              <Badge variant="outline" className="mt-1">{parent.status}</Badge>
            </div>
          </div>
        )}

        {predecessors && predecessors.length > 0 && (
          <div>
            <div className="text-sm font-semibold mb-2">Depends On</div>
            <div className="space-y-2">
              {predecessors.map((pred) => (
                <div key={pred.id} className="flex items-center gap-2 p-2 border rounded">
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <span className="flex-1">{pred.title}</span>
                  <Badge variant={pred.status === 'completed' ? 'default' : 'secondary'}>
                    {pred.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {subtasks && subtasks.length > 0 && (
          <div>
            <div className="text-sm font-semibold mb-2">Subtasks ({subtasks.length})</div>
            <div className="text-sm text-muted-foreground">
              {subtasks.filter(s => s.status === 'completed').length} / {subtasks.length} completed
            </div>
          </div>
        )}

        {!parent && (!predecessors || predecessors.length === 0) && (!subtasks || subtasks.length === 0) && (
          <div className="text-center py-8 text-muted-foreground">
            <p>No dependencies or subtasks</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DependencyVisualizer;
