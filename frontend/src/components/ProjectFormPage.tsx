// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectFormPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    project_type: 'improvement',
    priority: 'normal',
    planned_start: '',
    planned_end: '',
    budget: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post(`${API}/projects`, formData);
      navigate(`/projects/${response.data.id}`);
    } catch (err) {
      alert('Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Create Project" subtitle="New project">
      <form onSubmit={handleSubmit} className="max-w-3xl space-y-6">
        <Card>
          <CardHeader><CardTitle>Project Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2"><Label>Project Name *</Label><Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required /></div>
            <div className="space-y-2"><Label>Description</Label><Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} rows={4} /></div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Project Type</Label>
                <Select value={formData.project_type} onValueChange={(v) => setFormData({...formData, project_type: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="capital">Capital</SelectItem>
                    <SelectItem value="improvement">Improvement</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="strategic">Strategic</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Priority</Label>
                <Select value={formData.priority} onValueChange={(v) => setFormData({...formData, priority: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label>Planned Start</Label><Input type="date" value={formData.planned_start} onChange={(e) => setFormData({...formData, planned_start: e.target.value})} /></div>
              <div className="space-y-2"><Label>Planned End</Label><Input type="date" value={formData.planned_end} onChange={(e) => setFormData({...formData, planned_end: e.target.value})} /></div>
            </div>
            <div className="space-y-2"><Label>Budget ($)</Label><Input type="number" step="0.01" value={formData.budget} onChange={(e) => setFormData({...formData, budget: e.target.value})} /></div>
          </CardContent>
        </Card>
        <div className="flex gap-2">
          <Button type="button" variant="outline" onClick={() => navigate('/projects')} className="flex-1">Cancel</Button>
          <Button type="submit" disabled={loading} className="flex-1"><Save className="h-4 w-4 mr-2" />{loading ? 'Creating...' : 'Create Project'}</Button>
        </div>
      </form>
    </ModernPageWrapper>
  );
};

export default ProjectFormPage;
