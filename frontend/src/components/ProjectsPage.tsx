// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, FolderKanban, Target, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsRes, statsRes] = await Promise.all([
        axios.get(`${API}/projects`),
        axios.get(`${API}/projects/stats/overview`),
      ]);
      setProjects(projectsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-500',
      active: 'bg-blue-500',
      planning: 'bg-purple-500',
      on_hold: 'bg-yellow-500',
      cancelled: 'bg-red-500',
    };
    return <Badge className={colors[status] || 'bg-slate-500'}>{status}</Badge>;
  };

  const navigate = useNavigate();

  return (
    <ModernPageWrapper 
      title="Projects" 
      subtitle="Project portfolio management"
      actions={
        <Button onClick={() => navigate('/projects/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Projects</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_projects || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Active</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.by_status?.active || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Budget</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">${(stats?.total_budget || 0).toLocaleString()}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Actual Cost</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">${(stats?.total_actual_cost || 0).toLocaleString()}</div></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Projects ({projects.length})</CardTitle></CardHeader>
          <CardContent>
            {projects.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No projects yet</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project) => (
                  <Card key={project.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <CardTitle className="text-base">{project.name}</CardTitle>
                          <div className="text-sm text-muted-foreground mt-1">{project.project_code}</div>
                        </div>
                        {getStatusBadge(project.status)}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="text-sm">
                        <div><span className="text-muted-foreground">PM:</span> {project.project_manager_name}</div>
                        <div><span className="text-muted-foreground">Budget:</span> ${project.budget.toLocaleString()}</div>
                        <div><span className="text-muted-foreground">Progress:</span> {project.completion_percentage}%</div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default ProjectsPage;
