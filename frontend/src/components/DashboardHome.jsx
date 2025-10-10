import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  ClipboardCheck,
  CheckSquare,
  ListTodo,
  Users,
  TrendingUp,
  AlertCircle,
  Building2,
  BarChart3,
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardHome = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/dashboard/stats`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const quickStats = [
    {
      title: 'Pending Inspections',
      value: stats?.pending || 0,
      icon: ClipboardCheck,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: null,
    },
    {
      title: 'Completed Today',
      value: stats?.completed_today || 0,
      icon: CheckSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: null,
    },
    {
      title: 'Pass Rate',
      value: stats?.pass_rate ? `${stats.pass_rate}%` : '0%',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: null,
    },
    {
      title: 'Avg Score',
      value: stats?.average_score ? `${stats.average_score}%` : 'N/A',
      icon: BarChart3,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      change: null,
    },
  ];

  const quickActions = [
    {
      title: 'Start Inspection',
      description: 'Begin a new inspection from template',
      icon: ClipboardCheck,
      color: 'text-blue-600',
      onClick: () => navigate('/inspections'),
    },
    {
      title: 'View Organization',
      description: 'Manage organizational structure',
      icon: Building2,
      color: 'text-green-600',
      onClick: () => navigate('/organization'),
    },
    {
      title: 'Manage Templates',
      description: 'Create and edit inspection templates',
      icon: ListTodo,
      color: 'text-purple-600',
      onClick: () => navigate('/inspections'),
    },
    {
      title: 'View Reports',
      description: 'Analytics and performance reports',
      icon: BarChart3,
      color: 'text-orange-600',
      onClick: () => alert('Reports - Coming in Milestone 6!'),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white" data-testid="dashboard-welcome">
          Welcome back, {user?.name?.split(' ')[0]}!
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Here's what's happening with your operations today.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {quickStats.map((stat, index) => (
          <Card key={index} data-testid={`stat-card-${index}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loading ? '...' : stat.value}</div>
              {stat.change && (
                <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <Card
              key={index}
              className="cursor-pointer hover:shadow-lg transition-shadow group"
              onClick={action.onClick}
              data-testid={`quick-action-${index}`}
            >
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform`}>
                  <action.icon className={`h-6 w-6 ${action.color}`} />
                </div>
                <CardTitle className="text-lg">{action.title}</CardTitle>
                <CardDescription>{action.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates across your organization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats && stats.total_inspections > 0 ? (
              <div className="flex items-center gap-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                  <ClipboardCheck className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Inspection System Active</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {stats.total_inspections} total inspections completed
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No recent activity. Start by creating an inspection template!</p>
                <Button
                  onClick={() => navigate('/inspections')}
                  className="mt-4"
                  size="sm"
                >
                  Get Started
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardHome;