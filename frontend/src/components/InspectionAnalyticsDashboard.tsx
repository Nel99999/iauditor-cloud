// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  TrendingUp, TrendingDown, Clock, CheckCircle, XCircle,
  BarChart3, Calendar, AlertTriangle, Target
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  secondary: '#6366f1',
};

const InspectionAnalyticsDashboard = ({ templateId, templateName }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (templateId) {
      loadAnalytics();
    }
  }, [templateId]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/inspections/templates/${templateId}/analytics`);
      setAnalytics(response.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12 text-red-600">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analytics || analytics.total_executions === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12 text-muted-foreground">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-semibold mb-2">No Data Available</p>
            <p className="text-sm">Complete some inspections to see analytics</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const completionRate = analytics.total_executions > 0
    ? ((analytics.completed_executions / analytics.total_executions) * 100).toFixed(1)
    : 0;

  // Prepare data for pie chart
  const statusData = [
    { name: 'Completed', value: analytics.completed_executions, color: COLORS.success },
    { name: 'In Progress', value: analytics.in_progress_executions, color: COLORS.warning },
  ];

  // Pass/Fail data for pie chart
  const passedCount = Math.round((analytics.pass_rate / 100) * analytics.completed_executions);
  const failedCount = analytics.completed_executions - passedCount;
  const passFailData = [
    { name: 'Passed', value: passedCount, color: COLORS.success },
    { name: 'Failed', value: failedCount, color: COLORS.danger },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          Analytics Dashboard
        </h2>
        <p className="text-muted-foreground mt-1">
          Performance metrics for "{templateName || analytics.template_name}"
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.total_executions}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.completed_executions} completed, {analytics.in_progress_executions} in progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              {analytics.pass_rate}%
              {analytics.pass_rate >= 80 ? (
                <TrendingUp className="h-4 w-4 text-green-600" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-600" />
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {passedCount} passed, {failedCount} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.average_score ? `${analytics.average_score}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Average inspection score
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.average_duration_minutes ? `${analytics.average_duration_minutes}m` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Time to complete
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trends">Completion Trends</TabsTrigger>
          <TabsTrigger value="status">Status Distribution</TabsTrigger>
          <TabsTrigger value="findings">Common Findings</TabsTrigger>
        </TabsList>

        {/* Completion Trends Chart */}
        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>Completion Trend (Last 30 Days)</CardTitle>
              <CardDescription>Daily inspection completion count</CardDescription>
            </CardHeader>
            <CardContent>
              {analytics.completion_trend && analytics.completion_trend.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analytics.completion_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke={COLORS.primary} 
                      strokeWidth={2}
                      name="Completions"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <p>No completion data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Status Distribution Chart */}
        <TabsContent value="status">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Execution Status</CardTitle>
                <CardDescription>Completed vs In Progress</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Pass/Fail Distribution</CardTitle>
                <CardDescription>Success rate breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={passFailData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {passFailData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Common Findings */}
        <TabsContent value="findings">
          <Card>
            <CardHeader>
              <CardTitle>Most Common Findings</CardTitle>
              <CardDescription>Top 10 issues identified during inspections</CardDescription>
            </CardHeader>
            <CardContent>
              {analytics.most_common_findings && analytics.most_common_findings.length > 0 ? (
                <div className="space-y-4">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart 
                      data={analytics.most_common_findings.slice(0, 10)}
                      layout="vertical"
                      margin={{ left: 150 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis 
                        dataKey="finding" 
                        type="category" 
                        width={140}
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip />
                      <Bar dataKey="count" fill={COLORS.danger} />
                    </BarChart>
                  </ResponsiveContainer>

                  <Separator />

                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold">Findings List</h4>
                    {analytics.most_common_findings.map((finding, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-900 rounded">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{index + 1}</Badge>
                          <span className="text-sm">{finding.finding}</span>
                        </div>
                        <Badge variant="destructive">{finding.count}x</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No findings recorded yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Summary Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="text-sm text-muted-foreground">Completion Rate</div>
              <div className="text-2xl font-bold text-blue-600">{completionRate}%</div>
              <p className="text-xs text-muted-foreground mt-1">
                {analytics.completed_executions} of {analytics.total_executions} completed
              </p>
            </div>

            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <div className="text-sm text-muted-foreground">Quality Score</div>
              <div className="text-2xl font-bold text-green-600">
                {analytics.average_score ? `${analytics.average_score}%` : 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Average inspection quality
              </p>
            </div>

            <div className="p-4 bg-amber-50 dark:bg-amber-950/20 rounded-lg">
              <div className="text-sm text-muted-foreground">Issues Found</div>
              <div className="text-2xl font-bold text-amber-600">
                {analytics.most_common_findings?.reduce((sum, f) => sum + f.count, 0) || 0}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Total findings across all inspections
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InspectionAnalyticsDashboard;
