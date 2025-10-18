// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Package, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InventoryPage = () => {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [itemsRes, statsRes] = await Promise.all([
        axios.get(`${API}/inventory/items`),
        axios.get(`${API}/inventory/stats`),
      ]);
      setItems(itemsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Inventory" subtitle="Spare parts and stock management">
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Items</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_items || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Value</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">${(stats?.total_value || 0).toLocaleString()}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm text-amber-600">Below Reorder</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold text-amber-600">{stats?.items_below_reorder || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm text-red-600">Out of Stock</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold text-red-600">{stats?.out_of_stock || 0}</div></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Inventory Items ({items.length})</CardTitle></CardHeader>
          <CardContent>
            {items.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No inventory items yet</div>
            ) : (
              <div className="space-y-2">
                {items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">{item.description}</div>
                      <div className="text-sm text-muted-foreground">{item.part_number}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{item.quantity_available} {item.unit_of_measure}</div>
                      <div className="text-sm text-muted-foreground">${item.unit_cost}/unit</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default InventoryPage;
