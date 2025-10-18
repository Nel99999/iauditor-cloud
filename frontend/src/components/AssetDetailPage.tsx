// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Edit, QrCode, Package, Clock, Wrench, FileText, History } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssetDetailPage = () => {
  const navigate = useNavigate();
  const { assetId } = useParams();
  const [asset, setAsset] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [assetId]);

  const loadData = async () => {
    try {
      const [assetRes, historyRes] = await Promise.all([
        axios.get(`${API}/assets/${assetId}`),
        axios.get(`${API}/assets/${assetId}/history`),
      ]);
      setAsset(assetRes.data);
      setHistory(historyRes.data.history || []);
    } catch (err) {
      console.error('Failed to load asset:', err);
      alert('Asset not found');
      navigate('/assets');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQR = async () => {
    try {
      const response = await axios.post(`${API}/assets/${assetId}/qr-code`, {}, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `${asset.asset_tag}_qr.png`;
      link.click();
    } catch (err) {
      alert('Failed to generate QR code');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <ModernPageWrapper
      title={asset.name}
      subtitle={`Asset Tag: ${asset.asset_tag}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/assets')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Button variant="outline" size="sm" onClick={handleGenerateQR}>
            <QrCode className="h-4 w-4 mr-2" />
            QR Code
          </Button>
          <Button size="sm" onClick={() => navigate(`/assets/${assetId}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details"><Package className="h-4 w-4 mr-2" />Details</TabsTrigger>
            <TabsTrigger value="history"><History className="h-4 w-4 mr-2" />History</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader><CardTitle>Basic Information</CardTitle></CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div><span className="font-medium">Asset Tag:</span> {asset.asset_tag}</div>
                  <div><span className="font-medium">Name:</span> {asset.name}</div>
                  <div><span className="font-medium">Type:</span> {asset.asset_type}</div>
                  <div><span className="font-medium">Criticality:</span> {getCriticalityBadge(asset.criticality)}</div>
                  <div><span className="font-medium">Status:</span> <Badge>{asset.status}</Badge></div>
                  {asset.description && <div><span className="font-medium">Description:</span> {asset.description}</div>}
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Technical Details</CardTitle></CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {asset.make && <div><span className="font-medium">Make:</span> {asset.make}</div>}
                  {asset.model && <div><span className="font-medium">Model:</span> {asset.model}</div>}
                  {asset.serial_number && <div><span className="font-medium">Serial:</span> {asset.serial_number}</div>}
                  {asset.manufacturer && <div><span className="font-medium">Manufacturer:</span> {asset.manufacturer}</div>}
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Financial</CardTitle></CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {asset.purchase_cost && <div><span className="font-medium">Purchase Cost:</span> ${asset.purchase_cost.toLocaleString()}</div>}
                  {asset.current_value && <div><span className="font-medium">Current Value:</span> ${asset.current_value.toLocaleString()}</div>}
                  {asset.purchase_date && <div><span className="font-medium">Purchase Date:</span> {asset.purchase_date}</div>}
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Maintenance</CardTitle></CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {asset.maintenance_schedule && <div><span className="font-medium">Schedule:</span> {asset.maintenance_schedule}</div>}
                  {asset.last_maintenance && <div><span className="font-medium">Last:</span> {asset.last_maintenance}</div>}
                  {asset.next_maintenance && <div><span className="font-medium">Next:</span> {asset.next_maintenance}</div>}
                  {asset.requires_calibration && <div><span className="font-medium">Calibration:</span> {asset.calibration_frequency}</div>}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader><CardTitle>Asset History ({history.length} entries)</CardTitle></CardHeader>
              <CardContent>
                {history.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No history yet</div>
                ) : (
                  <div className="space-y-3">
                    {history.map((entry, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
                        <Badge variant="outline">{entry.entry_type}</Badge>
                        <div className="flex-1">
                          <div className="font-medium">{entry.entry_name}</div>
                          <div className="text-sm text-muted-foreground">{entry.timestamp?.substring(0, 10)}</div>
                        </div>
                        {entry.performed_by && <div className="text-sm text-muted-foreground">{entry.performed_by}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </ModernPageWrapper>
  );
};

const getCriticalityBadge = (crit) => {
  const colors = { A: 'bg-red-500', B: 'bg-amber-500', C: 'bg-green-500' };
  return <Badge className={colors[crit]  || 'bg-slate-500'}>{crit}</Badge>;
};

export default AssetDetailPage;
