// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertOctagon, Bell } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EmergenciesPage = () => {
  const [emergencies, setEmergencies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEmergencies();
  }, []);

  const loadEmergencies = async () => {
    try {
      const response = await axios.get(`${API}/emergencies`);
      setEmergencies(response.data);
    } catch (err) {
      console.error('Failed to load emergencies:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      critical: 'bg-red-600',
      high: 'bg-red-500',
      moderate: 'bg-amber-500',
      low: 'bg-yellow-500',
    };
    return <Badge className={colors[severity] || 'bg-slate-500'}>{severity}</Badge>;
  };

  return (
    <ModernPageWrapper title="Emergency Management" subtitle="Emergency response tracking">
      <div className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Emergencies ({emergencies.length})</CardTitle></CardHeader>
          <CardContent>
            {emergencies.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No emergencies reported</div>
            ) : (
              <div className="space-y-3">
                {emergencies.map((emergency) => (
                  <div key={emergency.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <AlertOctagon className="h-5 w-5 text-red-600" />
                        <span className="font-bold">{emergency.emergency_number}</span>
                        {getSeverityBadge(emergency.severity)}
                        <Badge variant="outline">{emergency.emergency_type}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">{emergency.location} • {emergency.occurred_at?.substring(0, 10)}</div>
                      <div className="text-sm mt-1">{emergency.description}</div>
                    </div>
                    <Badge className={emergency.status === 'resolved' ? 'bg-green-500' : 'bg-red-500'}>
                      {emergency.status}
                    </Badge>
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

export default EmergenciesPage;
