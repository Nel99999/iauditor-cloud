// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, AlertTriangle, Search, ListChecks, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IncidentDetailPage = () => {
  const navigate = useNavigate();
  const { incidentId } = useParams();
  const [incident, setIncident] = useState(null);
  const [showCAPADialog, setShowCAPADialog] = useState(false);
  const [capaData, setCapaData] = useState({ description: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [incidentId]);

  const loadData = async () => {
    try {
      const response = await axios.get(`${API}/incidents/${incidentId}`);
      setIncident(response.data);
    } catch (err) {
      console.error('Failed to load incident:', err);
      navigate('/incidents');
    } finally {
      setLoading(false);
    }
  };

  const handleStartInvestigation = async () => {
    try {
      await axios.post(`${API}/incidents/${incidentId}/investigate`, {
        investigator_ids: [],
      });
      loadData();
    } catch (err) {
      alert('Failed to start investigation');
    }
  };

  const handleCreateCAPA = async () => {
    try {
      await axios.post(`${API}/incidents/${incidentId}/corrective-action`, {
        description: capaData.description,
      });
      setShowCAPADialog(false);
      setCapaData({ description: '' });
      loadData();
    } catch (err) {
      alert('Failed to create CAPA');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  const getSeverityBadge = (severity) => {
    const colors = { critical: 'bg-red-600', serious: 'bg-red-500', moderate: 'bg-amber-500', minor: 'bg-yellow-500' };
    return <Badge className={colors[severity] || 'bg-slate-500'}>{severity}</Badge>;
  };

  return (
    <ModernPageWrapper
      title={incident.incident_number}
      subtitle={`Incident Report - ${incident.incident_type}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/incidents')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          {incident.investigation_status === 'not_started' && (
            <Button size="sm" onClick={handleStartInvestigation}>
              <Search className="h-4 w-4 mr-2" />
              Start Investigation
            </Button>
          )}
          <Dialog open={showCAPADialog} onOpenChange={setShowCAPADialog}>
            <DialogTrigger asChild>
              <Button size="sm">
                <ListChecks className="h-4 w-4 mr-2" />
                Create CAPA
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Create Corrective Action</DialogTitle></DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Corrective Action Description</Label>
                  <Textarea
                    value={capaData.description}
                    onChange={(e) => setCapaData({description: e.target.value})}
                    placeholder="Describe corrective/preventive action..."
                    rows={4}
                  />
                </div>
                <Button onClick={handleCreateCAPA} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  Create CAPA Task
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Severity</CardTitle></CardHeader>
            <CardContent>{getSeverityBadge(incident.severity)}</CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Status</CardTitle></CardHeader>
            <CardContent><Badge>{incident.status}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Investigation</CardTitle></CardHeader>
            <CardContent><Badge variant="outline">{incident.investigation_status}</Badge></CardContent>
          </Card>
        </div>

        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="investigation">Investigation</TabsTrigger>
            <TabsTrigger value="capa">CAPA ({incident.corrective_action_task_ids?.length || 0})</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <Card>
              <CardHeader><CardTitle>Incident Details</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div><span className="font-medium">Incident Type:</span> <Badge variant="outline">{incident.incident_type}</Badge></div>
                <div><span className="font-medium">Occurred At:</span> {incident.occurred_at}</div>
                <div><span className="font-medium">Location:</span> {incident.location}</div>
                <div><span className="font-medium">Reported By:</span> {incident.reporter_name}</div>
                <div className="pt-4 border-t">
                  <div className="font-medium mb-2">Description:</div>
                  <p className="text-sm">{incident.description}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="investigation">
            <Card>
              <CardHeader><CardTitle>Investigation Status</CardTitle></CardHeader>
              <CardContent>
                {incident.investigation_status === 'not_started' ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Investigation not started</p>
                    <Button className="mt-4" onClick={handleStartInvestigation}>
                      Start Investigation
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Badge className="bg-blue-500">Investigation In Progress</Badge>
                    <p className="text-sm text-muted-foreground">Investigation has been initiated for this incident.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="capa">
            <Card>
              <CardHeader><CardTitle>Corrective Actions</CardTitle></CardHeader>
              <CardContent>
                {(!incident.corrective_action_task_ids || incident.corrective_action_task_ids.length === 0) ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <ListChecks className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No corrective actions yet</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">{incident.corrective_action_task_ids.length} CAPA task(s) created</p>
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

export default IncidentDetailPage;
