import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileText, Download, Filter, BarChart3, Shield, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuditViewer = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
    result: '',
    start_date: '',
    end_date: '',
    limit: 100
  });

  useEffect(() => {
    loadLogs();
    loadStats();
  }, []);

  const loadLogs = async (customFilters = filters) => {
    try {
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams();
      
      Object.keys(customFilters).forEach(key => {
        if (customFilters[key]) {
          params.append(key, customFilters[key]);
        }
      });
      
      const response = await axios.get(`${API}/audit/logs?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLogs(response.data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/audit/stats?days=7`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const applyFilters = () => {
    loadLogs(filters);
    setShowFilters(false);
  };

  const clearFilters = () => {
    const clearedFilters = {
      action: '',
      resource_type: '',
      result: '',
      start_date: '',
      end_date: '',
      limit: 100
    };
    setFilters(clearedFilters);
    loadLogs(clearedFilters);
  };

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource Type', 'Resource ID', 'Result'].join(','),
      ...logs.map(log => [
        log.timestamp,
        log.user_name,
        log.action,
        log.resource_type,
        log.resource_id,
        log.result
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  const getResultIcon = (result) => {
    switch (result) {
      case 'granted':
      case 'success':
        return <CheckCircle2 className=\"h-4 w-4 text-green-600\" />;
      case 'denied':
      case 'failure':
        return <XCircle className=\"h-4 w-4 text-red-600\" />;
      default:
        return <AlertCircle className=\"h-4 w-4 text-yellow-600\" />;
    }
  };

  const getResultColor = (result) => {
    switch (result) {
      case 'granted':
      case 'success':
        return 'bg-green-100 text-green-700';
      case 'denied':
      case 'failure':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-yellow-100 text-yellow-700';
    }
  };

  return (
    <div className=\"space-y-6\">
      <div className=\"flex items-center justify-between\">
        <div>
          <h2 className=\"text-3xl font-bold text-slate-900 dark:text-white\">Audit Trail</h2>
          <p className=\"text-slate-600 dark:text-slate-400 mt-1\">
            Comprehensive audit logs and compliance reporting
          </p>
        </div>
        <div className=\"flex gap-2\">
          <Button variant=\"outline\" onClick={() => setShowFilters(!showFilters)}>
            <Filter className=\"h-4 w-4 mr-2\" />
            Filters
          </Button>
          <Button variant=\"outline\" onClick={exportLogs} disabled={logs.length === 0}>
            <Download className=\"h-4 w-4 mr-2\" />
            Export
          </Button>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
          <Card>
            <CardHeader className=\"pb-3\">
              <CardTitle className=\"text-sm font-medium\">Total Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"text-2xl font-bold\">{stats.total_logs}</div>
              <p className=\"text-xs text-slate-500\">Last 7 days</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className=\"pb-3\">
              <CardTitle className=\"text-sm font-medium\">Failed Permissions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"text-2xl font-bold text-red-600\">{stats.failed_permissions}</div>
              <p className=\"text-xs text-slate-500\">Access denied</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className=\"pb-3\">
              <CardTitle className=\"text-sm font-medium\">Active Users</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"text-2xl font-bold\">{stats.top_users.length}</div>
              <p className=\"text-xs text-slate-500\">With activity</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className=\"pb-3\">
              <CardTitle className=\"text-sm font-medium\">Top Action</CardTitle>
            </CardHeader>
            <CardContent>
              <div className=\"text-sm font-bold truncate\">
                {stats.actions[0]?.action || 'N/A'}
              </div>
              <p className=\"text-xs text-slate-500\">
                {stats.actions[0]?.count || 0} occurrences
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle>Filter Audit Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4\">
              <div>
                <Label>Action</Label>
                <Input
                  value={filters.action}
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                  placeholder=\"e.g., workflow.approve\"
                />
              </div>
              <div>
                <Label>Resource Type</Label>
                <Input
                  value={filters.resource_type}
                  onChange={(e) => handleFilterChange('resource_type', e.target.value)}
                  placeholder=\"e.g., inspection\"
                />
              </div>
              <div>
                <Label>Result</Label>
                <Select
                  value={filters.result}
                  onValueChange={(value) => handleFilterChange('result', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder=\"All results\" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value=\"all\">All results</SelectItem>
                    <SelectItem value=\"success\">Success</SelectItem>
                    <SelectItem value=\"failure\">Failure</SelectItem>
                    <SelectItem value=\"granted\">Granted</SelectItem>
                    <SelectItem value=\"denied\">Denied</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Start Date</Label>
                <Input
                  type=\"date\"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                />
              </div>
              <div>
                <Label>End Date</Label>
                <Input
                  type=\"date\"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                />
              </div>
              <div>
                <Label>Limit</Label>
                <Input
                  type=\"number\"
                  value={filters.limit}
                  onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
                  min={1}
                  max={1000}
                />
              </div>
            </div>
            <div className=\"flex gap-2 mt-4\">
              <Button onClick={applyFilters}>Apply Filters</Button>
              <Button variant=\"outline\" onClick={clearFilters}>Clear Filters</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Audit Logs */}
      {loading ? (
        <div className=\"text-center py-12\">
          <p className=\"text-slate-600 dark:text-slate-400\">Loading audit logs...</p>
        </div>
      ) : logs.length === 0 ? (
        <Card>
          <CardContent className=\"text-center py-12\">
            <Shield className=\"h-12 w-12 mx-auto mb-4 text-slate-400\" />
            <p className=\"text-slate-600 dark:text-slate-400\">
              No audit logs found. Try adjusting your filters.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Audit Logs ({logs.length})</CardTitle>
            <CardDescription>Recent system activities and security events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className=\"space-y-3\">
              {logs.map((log, idx) => (
                <div
                  key={log.id || idx}
                  className=\"flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg\"
                >
                  <div className=\"mt-1\">{getResultIcon(log.result)}</div>
                  <div className=\"flex-1 min-w-0\">
                    <div className=\"flex items-center gap-2 mb-1\">
                      <span className=\"font-semibold text-sm\">{log.user_name}</span>
                      <Badge className={getResultColor(log.result)}>{log.result}</Badge>
                      <span className=\"text-xs text-slate-500\">{log.action}</span>
                    </div>
                    <div className=\"text-sm text-slate-600 dark:text-slate-400\">
                      <span className=\"font-medium\">{log.resource_type}</span>: {log.resource_id}
                      {log.permission_checked && (
                        <span className=\"ml-2 text-xs\">
                          (Permission: {log.permission_checked})
                        </span>
                      )}
                    </div>
                    <div className=\"text-xs text-slate-500 mt-1\">
                      {formatDate(log.timestamp)}
                    </div>
                    {log.changes && (
                      <details className=\"text-xs mt-2\">
                        <summary className=\"cursor-pointer text-blue-600\">View changes</summary>
                        <pre className=\"mt-1 p-2 bg-slate-100 dark:bg-slate-900 rounded text-xs overflow-x-auto\">
                          {JSON.stringify(log.changes, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AuditViewer;
