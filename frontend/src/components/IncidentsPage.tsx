// @ts-nocheck
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IncidentsPage = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [incidentsRes, statsRes] = await Promise.all([
        axios.get(`${API}/incidents`),
        axios.get(`${API}/incidents/stats`),
      ]);
      setIncidents(incidentsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      critical: 'bg-red-600',
      serious: 'bg-red-500',
      moderate: 'bg-amber-500',
      minor: 'bg-yellow-500',
    };
    return <Badge className={colors[severity] || 'bg-slate-500'}>{severity}</Badge>;
  };

  return (
    <ModernPageWrapper title="Incidents" subtitle="Safety events and near-misses">
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Incidents</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_incidents || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">This Month</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.this_month || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Injuries</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.by_type?.injury || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Near Misses</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.by_type?.near_miss || 0}</div></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Recent Incidents ({incidents.length})</CardTitle></CardHeader>
          <CardContent>
            {incidents.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No incidents reported</div>
            ) : (
              <div className="space-y-3">
                {incidents.map((incident) => (
                  <div 
                    key={incident.id} 
                    className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                    onClick={() => navigate(`/incidents/${incident.id}`)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                        <span className="font-medium">{incident.incident_number}</span>
                        {getSeverityBadge(incident.severity)}
                        <Badge variant="outline">{incident.incident_type}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {incident.location} • {incident.occurred_at?.substring(0, 10)}
                      </div>
                      <div className="text-sm mt-1">{incident.description}</div>
                    </div>
                    <Badge>{incident.status}</Badge>
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

export default IncidentsPage;
