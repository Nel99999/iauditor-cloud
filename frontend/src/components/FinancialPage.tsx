// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FinancialPage = () => {
  const [summary, setSummary] = useState(null);
  const [capex, setCapex] = useState([]);
  const [opex, setOpex] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [summaryRes, capexRes, opexRes, budgetsRes] = await Promise.all([
        axios.get(`${API}/financial/summary`),
        axios.get(`${API}/financial/capex`),
        axios.get(`${API}/financial/opex`),
        axios.get(`${API}/financial/budgets`),
      ]);
      setSummary(summaryRes.data);
      setCapex(capexRes.data);
      setOpex(opexRes.data);
      setBudgets(budgetsRes.data);
    } catch (err) {
      console.error('Failed to load financial data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Financial Management" subtitle="Budget tracking and financial overview">
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><DollarSign className="h-5 w-5" />CAPEX</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="text-2xl font-bold">${(summary?.capex?.total_estimated || 0).toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">{summary?.capex?.total_requests || 0} requests</div>
              <div className="text-sm text-green-600">Approved: ${(summary?.capex?.approved_amount || 0).toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><DollarSign className="h-5 w-5" />OPEX</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="text-2xl font-bold">${(summary?.opex?.total_spent || 0).toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">{summary?.opex?.total_transactions || 0} transactions</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><DollarSign className="h-5 w-5" />Budget</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <div className="text-2xl font-bold">${(summary?.budgets?.total_budget || 0).toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Spent: ${(summary?.budgets?.total_spent || 0).toLocaleString()}</div>
              <div className="text-sm flex items-center gap-1">
                {(summary?.budgets?.variance || 0) >= 0 ? (
                  <><TrendingUp className="h-4 w-4 text-green-600" /><span className="text-green-600">Variance: ${summary?.budgets?.variance?.toLocaleString()}</span></>
                ) : (
                  <><TrendingDown className="h-4 w-4 text-red-600" /><span className="text-red-600">Over: ${Math.abs(summary?.budgets?.variance || 0).toLocaleString()}</span></>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader><CardTitle>Recent CAPEX Requests ({capex.length})</CardTitle></CardHeader>
            <CardContent>
              {capex.slice(0, 5).map((c) => (
                <div key={c.id} className="flex justify-between p-2 border-b">
                  <div>
                    <div className="font-medium">{c.title}</div>
                    <div className="text-sm text-muted-foreground">{c.capex_number}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">${c.estimated_cost.toLocaleString()}</div>
                    <Badge variant="outline">{c.approval_status}</Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Recent OPEX ({opex.length})</CardTitle></CardHeader>
            <CardContent>
              {opex.slice(0, 5).map((o) => (
                <div key={o.id} className="flex justify-between p-2 border-b">
                  <div>
                    <div className="font-medium">{o.description}</div>
                    <div className="text-sm text-muted-foreground">{o.category}</div>
                  </div>
                  <div className="font-bold">${o.amount.toLocaleString()}</div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </ModernPageWrapper>
  );
};

export default FinancialPage;
