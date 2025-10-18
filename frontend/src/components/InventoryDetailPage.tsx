// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Package, Plus, Minus, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InventoryDetailPage = () => {
  const navigate = useNavigate();
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [showAdjustDialog, setShowAdjustDialog] = useState(false);
  const [adjustment, setAdjustment] = useState({ adjustment: '', notes: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [itemId]);

  const loadData = async () => {
    try {
      const response = await axios.get(`${API}/inventory/items/${itemId}`);
      setItem(response.data);
    } catch (err) {
      console.error('Failed to load item:', err);
      navigate('/inventory');
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustStock = async () => {
    try {
      await axios.post(`${API}/inventory/items/${itemId}/adjust`, {
        adjustment: parseFloat(adjustment.adjustment),
        notes: adjustment.notes,
      });
      setShowAdjustDialog(false);
      setAdjustment({ adjustment: '', notes: '' });
      loadData();
    } catch (err) {
      alert('Failed to adjust stock');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  const isLowStock = item.quantity_available <= item.reorder_point;

  return (
    <ModernPageWrapper
      title={item.description}
      subtitle={`Part Number: ${item.part_number}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/inventory')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Dialog open={showAdjustDialog} onOpenChange={setShowAdjustDialog}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Package className="h-4 w-4 mr-2" />
                Adjust Stock
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Adjust Stock Quantity</DialogTitle></DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Adjustment (+ to add, - to remove)</Label>
                  <Input
                    type="number"
                    placeholder="e.g., +10 or -5"
                    value={adjustment.adjustment}
                    onChange={(e) => setAdjustment({...adjustment, adjustment: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Input
                    value={adjustment.notes}
                    onChange={(e) => setAdjustment({...adjustment, notes: e.target.value})}
                    placeholder="Reason for adjustment"
                  />
                </div>
                <Button onClick={handleAdjustStock} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  Confirm Adjustment
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">On Hand</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{item.quantity_on_hand}</div>
              <div className="text-xs text-muted-foreground">{item.unit_of_measure}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Available</CardTitle></CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${isLowStock ? 'text-red-600' : ''}`}>
                {item.quantity_available}
              </div>
              {isLowStock && <Badge variant="destructive" className="mt-1">Low Stock</Badge>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Unit Cost</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">${item.unit_cost}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Value</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">${item.total_value.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Stock Information</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="font-medium">Category:</span><span>{item.category || 'N/A'}</span></div>
              <div className="flex justify-between"><span className="font-medium">Sub-Category:</span><span>{item.sub_category || 'N/A'}</span></div>
              <div className="flex justify-between"><span className="font-medium">Reorder Point:</span><span>{item.reorder_point} {item.unit_of_measure}</span></div>
              <div className="flex justify-between"><span className="font-medium">Reorder Quantity:</span><span>{item.reorder_quantity} {item.unit_of_measure}</span></div>
              {item.warehouse_id && <div className="flex justify-between"><span className="font-medium">Warehouse:</span><span>{item.warehouse_id}</span></div>}
              {item.bin_location && <div className="flex justify-between"><span className="font-medium">Bin Location:</span><span>{item.bin_location}</span></div>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Stock Levels</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-blue-50 dark:bg-blue-950/20 rounded">
                  <span className="text-sm">Quantity on Hand</span>
                  <span className="font-bold">{item.quantity_on_hand} {item.unit_of_measure}</span>
                </div>
                <div className="flex justify-between p-3 bg-amber-50 dark:bg-amber-950/20 rounded">
                  <span className="text-sm">Quantity Reserved</span>
                  <span className="font-bold">{item.quantity_reserved} {item.unit_of_measure}</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 dark:bg-green-950/20 rounded">
                  <span className="text-sm">Quantity Available</span>
                  <span className="font-bold">{item.quantity_available} {item.unit_of_measure}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ModernPageWrapper>
  );
};

export default InventoryDetailPage;
