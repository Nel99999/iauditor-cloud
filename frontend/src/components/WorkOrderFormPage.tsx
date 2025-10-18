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

const WorkOrderFormPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    work_type: 'corrective',
    priority: 'normal',
    asset_id: '',
    estimated_hours: '',
  });
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      const response = await axios.get(`${API}/assets`);
      setAssets(response.data);
    } catch (err) {
      console.error('Failed to load assets:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await axios.post(`${API}/work-orders`, formData);
      navigate('/work-orders');
    } catch (err) {
      alert('Failed to create work order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Create Work Order" subtitle="New maintenance work order">
      <form onSubmit={handleSubmit} className="max-w-3xl space-y-6">
        <Card>
          <CardHeader><CardTitle>Work Order Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2"><Label>Title *</Label><Input value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} required /></div>
            <div className="space-y-2"><Label>Description</Label><Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} rows={4} /></div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Work Type</Label>
                <Select value={formData.work_type} onValueChange={(v) => setFormData({...formData, work_type: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="corrective">Corrective</SelectItem>
                    <SelectItem value="preventive">Preventive</SelectItem>
                    <SelectItem value="predictive">Predictive</SelectItem>
                    <SelectItem value="emergency">Emergency</SelectItem>
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
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Asset</Label>
                <Select value={formData.asset_id} onValueChange={(v) => setFormData({...formData, asset_id: v})}>
                  <SelectTrigger><SelectValue placeholder="Select asset" /></SelectTrigger>
                  <SelectContent>
                    {assets.map(a => <SelectItem key={a.id} value={a.id}>{a.name} ({a.asset_tag})</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2"><Label>Estimated Hours</Label><Input type="number" step="0.5" value={formData.estimated_hours} onChange={(e) => setFormData({...formData, estimated_hours: e.target.value})} /></div>
            </div>
          </CardContent>
        </Card>
        <div className="flex gap-2">
          <Button type="button" variant="outline" onClick={() => navigate('/work-orders')} className="flex-1">Cancel</Button>
          <Button type="submit" disabled={loading} className="flex-1"><Save className="h-4 w-4 mr-2" />{loading ? 'Creating...' : 'Create Work Order'}</Button>
        </div>
      </form>
    </ModernPageWrapper>
  );
};

export default WorkOrderFormPage;
