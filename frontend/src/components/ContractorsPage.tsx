// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, Building2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ContractorsPage = () => {
  const [contractors, setContractors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContractors();
  }, []);

  const loadContractors = async () => {
    try {
      const response = await axios.get(`${API}/contractors`);
      setContractors(response.data);
    } catch (err) {
      console.error('Failed to load contractors:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Contractors" subtitle="Vendor and contractor management">
      <div className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Active Contractors ({contractors.length})</CardTitle></CardHeader>
          <CardContent>
            {contractors.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No contractors yet</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {contractors.map((contractor) => (
                  <Card key={contractor.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-5 w-5 text-primary" />
                        <CardTitle className="text-base">{contractor.company_name}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div><span className="text-muted-foreground">Contact:</span> {contractor.contact_person}</div>
                      <div><span className="text-muted-foreground">Email:</span> {contractor.email}</div>
                      <div><span className="text-muted-foreground">Type:</span> <Badge variant="outline">{contractor.contractor_type}</Badge></div>
                      {contractor.trade && <div><span className="text-muted-foreground">Trade:</span> {contractor.trade}</div>}
                      <div><span className="text-muted-foreground">Performance:</span> {contractor.performance_score}/100</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default ContractorsPage;
