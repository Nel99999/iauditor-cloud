import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import {
  Activity, TrendingUp, Users, CheckSquare, Clock, Award,
  Download, RefreshCw
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

const AnalyticsDashboard = () => {
  const [period, setPeriod] = useState('week');
  const [overview, setOverview] = useState<any | null>(null);
  const [taskTrends, setTaskTrends] = useState<any[]>([]);
  const [tasksByStatus, setTasksByStatus] = useState<any[]>([]);
  const [tasksByPriority, setTasksByPriority] = useState<any[]>([]);
  const [timeTrackingTrends, setTimeTrackingTrends] = useState<any[]>([]);
  const [userActivity, setUserActivity] = useState<any[]>([]);
  const [_loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchAnalyticsData = async (showRefresh = false) => {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch all analytics data in parallel
      const [
        overviewRes,
        trendsRes,
        statusRes,
        priorityRes,
        timeRes,
        activityRes
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/analytics/overview?period=${period}`, { headers }),
        axios.get(`${API_BASE_URL}/api/analytics/tasks/trends?period=${period}`, { headers }),
        axios.get(`${API_BASE_URL}/api/analytics/tasks/by-status`, { headers }),
        axios.get(`${API_BASE_URL}/api/analytics/tasks/by-priority`, { headers }),
        axios.get(`${API_BASE_URL}/api/analytics/time-tracking/trends?period=${period}`, { headers }),
        axios.get(`${API_BASE_URL}/api/analytics/user-activity?limit=5`, { headers })
      ]);

      setOverview(overviewRes.data);
      
      // Format task trends data for charts
      if (trendsRes.data.trends) {
        setTaskTrends(trendsRes.data.trends.map((item: any) => ({
          date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          created: item.created || 0,
          completed: item.completed || 0
        })));
      }

      // Format status data for pie chart
      if (statusRes.data.breakdown) {
        setTasksByStatus(Object.entries(statusRes.data.breakdown).map(([status, count]: [string, any]) => ({
          name: status.replace('_', ' ').toUpperCase(),
          value: count
        })));
      }

      // Format priority data for bar chart
      if (priorityRes.data.breakdown) {
        setTasksByPriority(Object.entries(priorityRes.data.breakdown).map(([priority, count]: [string, any]) => ({
          name: priority.toUpperCase(),
          count: count
        })));
      }

      // Format time tracking trends
      if (timeRes.data.trends) {
        setTimeTrackingTrends(timeRes.data.trends.map((item: any) => ({
          date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          hours: item.total_hours || 0,
          billable: item.billable_hours || 0
        })));
      }

      // Format user activity
      if (activityRes.data.most_active_users) {
        setUserActivity(activityRes.data.most_active_users.slice(0, 5));
      }

    } catch (err: unknown) {
      console.error('Error fetching analytics:', err);
      setError((err as any).response?.data?.detail || 'Failed to load analytics data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, [period]);

  const handleRefresh = () => {
    fetchAnalyticsData(true);
  };

  const exportData = () => {
    const exportData = {
      period,
      generated_at: new Date().toISOString(),
      overview,
      taskTrends,
      tasksByStatus,
      tasksByPriority,
      timeTrackingTrends,
      userActivity
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${period}-${Date.now()}.json`;
    a.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-5 h-5 text-red-600" />
              <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">Error Loading Analytics</h3>
            </div>
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => fetchAnalyticsData()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Activity className="w-8 h-8 text-blue-600" />
              Analytics Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Comprehensive insights and performance metrics
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Period Selector */}
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
            </select>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>

            {/* Export Button */}
            <button
              onClick={exportData}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Overview Metrics */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <CheckSquare className="w-8 h-8 text-blue-600" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Tasks</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {overview.metrics?.tasks?.total || 0}
              </div>
              <div className="text-sm text-green-600 mt-1">
                {overview.metrics?.tasks?.completed || 0} completed
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <Clock className="w-8 h-8 text-green-600" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Time Tracked</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {overview.metrics?.time_tracking?.total_hours?.toFixed(1) || 0}h
              </div>
              <div className="text-sm text-blue-600 mt-1">
                {overview.metrics?.time_tracking?.billable_hours?.toFixed(1) || 0}h billable
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-8 h-8 text-purple-600" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Active Users</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {overview.metrics?.users?.active || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                of {overview.metrics?.users?.total || 0} total
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <Award className="w-8 h-8 text-yellow-600" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Inspections</span>
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {overview.metrics?.inspections?.total || 0}
              </div>
              <div className="text-sm text-green-600 mt-1">
                {overview.metrics?.inspections?.pass_rate?.toFixed(0) || 0}% pass rate
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Task Trends Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Task Trends
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={taskTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem'
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="created" stroke="#3b82f6" strokeWidth={2} name="Created" />
                <Line type="monotone" dataKey="completed" stroke="#10b981" strokeWidth={2} name="Completed" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Tasks by Status (Pie Chart) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tasks by Status</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tasksByStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {tasksByStatus.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Tasks by Priority (Bar Chart) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tasks by Priority</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tasksByPriority}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem'
                  }}
                />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Time Tracking Trends (Area Chart) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-green-600" />
              Time Tracking Trends
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={timeTrackingTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.5rem'
                  }}
                />
                <Legend />
                <Area type="monotone" dataKey="hours" stackId="1" stroke="#10b981" fill="#10b981" name="Total Hours" />
                <Area type="monotone" dataKey="billable" stackId="2" stroke="#3b82f6" fill="#3b82f6" name="Billable Hours" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Users Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-600" />
            Top Active Users
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">User</th>
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">Tasks Completed</th>
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">Time Logged</th>
                  <th className="text-left py-3 px-4 text-gray-600 dark:text-gray-400 font-medium">Last Active</th>
                </tr>
              </thead>
              <tbody>
                {userActivity.length > 0 ? (
                  userActivity.map((user: any, index: number) => (
                    <tr key={index} className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{user.user_name || 'N/A'}</td>
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{user.tasks_completed || 0}</td>
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{user.hours_logged?.toFixed(1) || 0}h</td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">
                        {user.last_activity ? new Date(user.last_activity).toLocaleDateString() : 'N/A'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-gray-500 dark:text-gray-400">
                      No user activity data available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
