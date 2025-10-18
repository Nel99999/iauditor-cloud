// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Search, Eye, Edit, Trash2, QrCode, Package, TrendingUp, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssetsPage = () => {
  const navigate = useNavigate();
  const [assets, setAssets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [criticalityFilter, setCriticalityFilter] = useState('all');

  useEffect(() => {
    loadData();
  }, [typeFilter, criticalityFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (typeFilter !== 'all') params.asset_type = typeFilter;
      if (criticalityFilter !== 'all') params.criticality = criticalityFilter;
      if (search) params.search = search;
      
      const [assetsRes, statsRes] = await Promise.all([
        axios.get(`${API}/assets`, { params }),
        axios.get(`${API}/assets/stats`),
      ]);
      setAssets(assetsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load assets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (assetId) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;
    try {
      await axios.delete(`${API}/assets/${assetId}`);
      loadData();
    } catch (err) {
      alert('Failed to delete asset');
    }
  };

  const getCriticalityBadge = (crit) => {
    const colors = { A: 'bg-red-500', B: 'bg-amber-500', C: 'bg-green-500' };
    return <Badge className={colors[crit] || 'bg-slate-500'}>{crit}</Badge>;
  };

  return (
    <ModernPageWrapper
      title="Asset Register"
      subtitle="Manage organizational assets"
      actions={
        <Button onClick={() => navigate('/assets/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Asset
        </Button>
      }
    >
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Total Assets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_assets || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Total Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(stats?.total_value || 0).toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-amber-600">Maintenance Due</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-600">{stats?.maintenance_due_count || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-red-600">Calibration Due</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats?.calibration_due_count || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search assets..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && loadData()}
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="equipment">Equipment</SelectItem>
                  <SelectItem value="vehicle">Vehicle</SelectItem>
                  <SelectItem value="building">Building</SelectItem>
                  <SelectItem value="machinery">Machinery</SelectItem>
                </SelectContent>
              </Select>
              <Select value={criticalityFilter} onValueChange={setCriticalityFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Criticality</SelectItem>
                  <SelectItem value="A">Critical (A)</SelectItem>
                  <SelectItem value="B">Important (B)</SelectItem>
                  <SelectItem value="C">Normal (C)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Asset Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : assets.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Package className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-semibold mb-2">No assets yet</h3>
                <Button onClick={() => navigate('/assets/new')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Asset
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assets.map((asset) => (
              <Card key={asset.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <CardTitle className="text-base">{asset.name}</CardTitle>
                        {getCriticalityBadge(asset.criticality)}
                      </div>
                      <div className="text-sm text-muted-foreground">{asset.asset_tag}</div>
                    </div>
                    <Badge variant="outline" className="capitalize">{asset.asset_type}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm space-y-1">
                    {asset.make && <div><span className="text-muted-foreground">Make:</span> {asset.make}</div>}
                    {asset.model && <div><span className="text-muted-foreground">Model:</span> {asset.model}</div>}
                    {asset.serial_number && <div><span className="text-muted-foreground">S/N:</span> {asset.serial_number}</div>}
                    {asset.unit_name && <div><span className="text-muted-foreground">Unit:</span> {asset.unit_name}</div>}
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => navigate(`/assets/${asset.id}`)} className="flex-1">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => navigate(`/assets/${asset.id}/edit`)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDelete(asset.id)} className="text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </ModernPageWrapper>
  );
};

export default AssetsPage;
