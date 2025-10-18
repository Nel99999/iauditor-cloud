// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { ArrowLeft, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssetFormPage = () => {
  const navigate = useNavigate();
  const { assetId } = useParams();
  const isEdit = !!assetId;

  const [formData, setFormData] = useState({
    asset_tag: '',
    name: '',
    description: '',
    asset_type: 'equipment',
    category: '',
    criticality: 'C',
    unit_id: '',
    location_details: '',
    make: '',
    model: '',
    serial_number: '',
    manufacturer: '',
    purchase_date: '',
    purchase_cost: '',
    status: 'active',
    maintenance_schedule: 'monthly',
    requires_calibration: false,
  });
  
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUnits();
    if (isEdit) {
      loadAsset();
    }
  }, [assetId]);

  const loadUnits = async () => {
    try {
      const response = await axios.get(`${API}/organizations/units`);
      setUnits(response.data);
    } catch (err) {
      console.error('Failed to load units:', err);
    }
  };

  const loadAsset = async () => {
    try {
      const response = await axios.get(`${API}/assets/${assetId}`);
      setFormData(response.data);
    } catch (err) {
      alert('Failed to load asset');
      navigate('/assets');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.asset_tag || !formData.name) {
      alert('Asset tag and name are required');
      return;
    }

    try {
      setLoading(true);
      if (isEdit) {
        await axios.put(`${API}/assets/${assetId}`, formData);
      } else {
        await axios.post(`${API}/assets`, formData);
      }
      navigate('/assets');
    } catch (err) {
      alert('Failed to save asset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper
      title={isEdit ? 'Edit Asset' : 'Create Asset'}
      subtitle={isEdit ? 'Update asset information' : 'Add new asset to register'}
      actions={
        <Button variant="outline" size="sm" onClick={() => navigate('/assets')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
      }
    >
      <form onSubmit={handleSubmit} className=\"max-w-4xl space-y-6\">
        <Card>
          <CardHeader><CardTitle>Basic Information</CardTitle></CardHeader>
          <CardContent className=\"space-y-4\">
            <div className=\"grid grid-cols-2 gap-4\">
              <div className=\"space-y-2\">
                <Label>Asset Tag *</Label>
                <Input value={formData.asset_tag} onChange={(e) => setFormData({...formData, asset_tag: e.target.value})} />
              </div>
              <div className=\"space-y-2\">
                <Label>Name *</Label>
                <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
              </div>
            </div>
            <div className=\"space-y-2\">
              <Label>Description</Label>
              <Textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} rows={3} />
            </div>
            <div className=\"grid grid-cols-3 gap-4\">
              <div className=\"space-y-2\">
                <Label>Type</Label>
                <Select value={formData.asset_type} onValueChange={(v) => setFormData({...formData, asset_type: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value=\"equipment\">Equipment</SelectItem>
                    <SelectItem value=\"vehicle\">Vehicle</SelectItem>
                    <SelectItem value=\"building\">Building</SelectItem>
                    <SelectItem value=\"machinery\">Machinery</SelectItem>
                    <SelectItem value=\"tools\">Tools</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className=\"space-y-2\">
                <Label>Criticality</Label>
                <Select value={formData.criticality} onValueChange={(v) => setFormData({...formData, criticality: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value=\"A\">A - Critical</SelectItem>
                    <SelectItem value=\"B\">B - Important</SelectItem>
                    <SelectItem value=\"C\">C - Normal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className=\"space-y-2\">
                <Label>Unit</Label>
                <Select value={formData.unit_id || ''} onValueChange={(v) => setFormData({...formData, unit_id: v})}>
                  <SelectTrigger><SelectValue placeholder=\"Select unit\" /></SelectTrigger>
                  <SelectContent>
                    {units.map(u => <SelectItem key={u.id} value={u.id}>{u.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Technical Details</CardTitle></CardHeader>
          <CardContent className=\"space-y-4\">
            <div className=\"grid grid-cols-2 gap-4\">
              <div className=\"space-y-2\"><Label>Make</Label><Input value={formData.make || ''} onChange={(e) => setFormData({...formData, make: e.target.value})} /></div>
              <div className=\"space-y-2\"><Label>Model</Label><Input value={formData.model || ''} onChange={(e) => setFormData({...formData, model: e.target.value})} /></div>
              <div className=\"space-y-2\"><Label>Serial Number</Label><Input value={formData.serial_number || ''} onChange={(e) => setFormData({...formData, serial_number: e.target.value})} /></div>
              <div className=\"space-y-2\"><Label>Manufacturer</Label><Input value={formData.manufacturer || ''} onChange={(e) => setFormData({...formData, manufacturer: e.target.value})} /></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Maintenance</CardTitle></CardHeader>
          <CardContent className=\"space-y-4\">
            <div className=\"grid grid-cols-2 gap-4\">
              <div className=\"space-y-2\">
                <Label>Schedule</Label>
                <Select value={formData.maintenance_schedule || 'monthly'} onValueChange={(v) => setFormData({...formData, maintenance_schedule: v})}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value=\"weekly\">Weekly</SelectItem>
                    <SelectItem value=\"monthly\">Monthly</SelectItem>
                    <SelectItem value=\"quarterly\">Quarterly</SelectItem>
                    <SelectItem value=\"annual\">Annual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className=\"space-y-2\">
                <Label className=\"flex items-center gap-2\">
                  Requires Calibration
                  <Switch checked={formData.requires_calibration} onCheckedChange={(c) => setFormData({...formData, requires_calibration: c})} />
                </Label>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className=\"flex gap-2\">
          <Button type=\"button\" variant=\"outline\" onClick={() => navigate('/assets')} className=\"flex-1\">Cancel</Button>
          <Button type=\"submit\" disabled={loading} className=\"flex-1\">
            <Save className=\"h-4 w-4 mr-2\" />
            {loading ? 'Saving...' : 'Save Asset'}
          </Button>
        </div>
      </form>
    </ModernPageWrapper>
  );
};

const getCriticalityBadge = (crit) => {
  const colors = { A: 'bg-red-500', B: 'bg-amber-500', C: 'bg-green-500' };
  return <Badge className={colors[crit] || 'bg-slate-500'}>{crit}</Badge>;
};

export default AssetFormPage;
