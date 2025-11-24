import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GlassCard, Button, Spinner } from '@/design-system/components';
import { motion } from 'framer-motion';
import {
  ClipboardCheck,
  CheckSquare,
  Users,
  TrendingUp,
  BarChart3,
  LucideIcon
} from 'lucide-react';
import MyWorkDashboard from './MyWorkDashboard';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

interface DashboardStats {
  users?: {
    total_users?: number;
    active_users?: number;
    pending_invitations?: number;
    recent_logins?: number;
  };
  tasks?: {
    active?: number;
    total_tasks?: number;
    todo?: number;
    in_progress?: number;
    completed?: number;
    overdue?: number;
    completion_rate?: number;
  };
  inspections?: {
    total?: number;
    pending?: number;
    completed_today?: number;
    pass_rate?: number;
    average_score?: number;
  };
  checklists?: {
    total_checklists?: number;
    completed_today?: number;
    pending_today?: number;
    completion_rate?: number;
  };
  organization?: {
    total_units?: number;
    total_levels?: number;
  };
}

interface QuickStat {
  title: string;
  value: number | string;
  icon: LucideIcon;
  color: string;
  change: string;
  link?: string;
}

interface Activity {
  title: string;
  description: string;
  time: string;
  icon: LucideIcon;
  link?: string;
}

import SyncService from '../services/SyncService';
import OfflineStorageService from '../services/OfflineStorageService';
import { RefreshCw } from 'lucide-react';

const DashboardHomeNew = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [pendingSyncCount, setPendingSyncCount] = useState<number>(0);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  // If user is not an admin/developer/manager, show the simplified "My Work" dashboard
  const isFieldWorker = user && !['admin', 'developer', 'manager'].includes(user.role);

  useEffect(() => {
    if (!isFieldWorker) {
      loadStats();
      loadRecentActivity();
    } else {
      setLoading(false);
    }

    // Check for pending offline items
    checkPendingSync();

    // Listen for online status to auto-sync or prompt
    window.addEventListener('online', checkPendingSync);
    return () => window.removeEventListener('online', checkPendingSync);
  }, [isFieldWorker]);

  const checkPendingSync = () => {
    const inspections = OfflineStorageService.getOfflineInspections();
    const pending = inspections.filter(i => !i.synced && i.status === 'completed').length;
    setPendingSyncCount(pending);
  };

  const handleSync = async () => {
    try {
      setIsSyncing(true);
      const result = await SyncService.syncPendingInspections();
      if (result.synced > 0) {
        alert(`Successfully synced ${result.synced} inspections!`);
      } else if (result.errors > 0) {
        alert(`Failed to sync ${result.errors} inspections. Please try again.`);
      } else {
        alert('All up to date!');
      }
      checkPendingSync();

      // Refresh stats if online
      if (!isFieldWorker && navigator.onLine) {
        loadStats();
        loadRecentActivity();
      }
    } catch (error) {
      console.error("Sync failed:", error);
      alert("Sync failed");
    } finally {
      setIsSyncing(false);
    }
  };

  const loadStats = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get<DashboardStats>(`${API}/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentActivity = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/users/me/recent-activity?limit=5`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const activities = (response.data || []).map((item: any) => {
        let icon = ClipboardCheck;
        let link = '/';

        if (item.resource_type === 'task') {
          icon = CheckSquare;
          link = '/tasks';
        } else if (item.resource_type === 'inspection') {
          icon = ClipboardCheck;
          link = '/inspections';
        } else if (item.resource_type === 'user') {
          icon = Users;
          link = '/users';
        }

        return {
          title: item.action || 'Activity',
          description: item.details || item.resource_type || '',
          time: item.created_at ? new Date(item.created_at).toLocaleString() : '',
          icon,
          link
        };
      });

      setRecentActivity(activities);
    } catch (err) {
      console.error('Failed to load recent activity:', err);
      setRecentActivity([]);
    }
  };

  if (isFieldWorker) {
    return <MyWorkDashboard />;
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="xl" />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  const quickStats: QuickStat[] = [
    {
      title: 'Total Users',
      value: stats?.users?.total_users || 0,
      icon: Users,
      color: 'blue',
      change: '+12%',
      link: '/users',
    },
    {
      title: 'Active Tasks',
      value: stats?.tasks?.active || 0,
      icon: CheckSquare,
      color: 'green',
      change: '+5%',
      link: '/tasks',
    },
    {
      title: 'Inspections',
      value: stats?.inspections?.total || 0,
      icon: ClipboardCheck,
      color: 'purple',
      change: '+8%',
      link: '/inspections',
    },
    {
      title: 'Completion Rate',
      value: `${stats?.tasks?.completion_rate || 0}%`,
      icon: TrendingUp,
      color: 'orange',
      change: '+3%',
      link: '/tasks',
    },
  ];

  return (
    <div className="dashboard-home-new">
      {/* Animated Background */}
      <div className="dashboard-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      {/* Welcome Header */}
      <motion.div
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center w-full">
          <div>
            <h1 className="dashboard-title">
              Welcome back, {user?.name || 'User'}! 👋
            </h1>
            <p className="dashboard-subtitle">
              Here's what's happening with your operations today
            </p>
          </div>
          {pendingSyncCount > 0 && (
            <Button
              onClick={handleSync}
              disabled={isSyncing}
              className="bg-yellow-500 hover:bg-yellow-600 text-white animate-pulse"
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
              Sync {pendingSyncCount} Items
            </Button>
          )}
        </div>
      </motion.div>

      {/* Quick Stats Grid */}
      <div className="stats-grid">
        {quickStats.map((stat: any, index: number) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              onClick={() => stat.link && navigate(stat.link)}
              style={{ cursor: stat.link ? 'pointer' : 'default' }}
            >
              <GlassCard hover className="stat-card">
                <div className="stat-icon-wrapper" style={{ '--stat-color': `var(--color-${stat.color})` } as React.CSSProperties}>
                  <Icon size={24} />
                </div>
                <div className="stat-content">
                  <p className="stat-label">{stat.title}</p>
                  <h3 className="stat-value">{stat.value}</h3>
                  <p className="stat-change positive">{stat.change}</p>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content-grid">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <GlassCard padding="lg" className="activity-card">
            <div className="card-header">
              <h2 className="card-title">Recent Activity</h2>
              <Button variant="ghost" size="sm">View All</Button>
            </div>
            <div className="activity-list">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity: any, index: number) => {
                  const Icon = activity.icon;
                  return (
                    <motion.div
                      key={index}
                      className="activity-item"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      onClick={() => activity.link && navigate(activity.link)}
                      style={{ cursor: activity.link ? 'pointer' : 'default' }}
                    >
                      <div className="activity-icon">
                        <Icon size={20} />
                      </div>
                      <div className="activity-content">
                        <p className="activity-title">{activity.title}</p>
                        <p className="activity-description">{activity.description}</p>
                      </div>
                      <p className="activity-time">{activity.time}</p>
                    </motion.div>
                  );
                })
              ) : (
                <p style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                  No recent activity
                </p>
              )}
            </div>
          </GlassCard>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <GlassCard padding="lg" className="quick-actions-card">
            <h2 className="card-title">Quick Actions</h2>
            <div className="quick-actions-list">
              <Button
                variant="primary"
                size="lg"
                onClick={() => navigate('/tasks')}
                icon={<CheckSquare size={20} />}
                className="action-button"
              >
                Create Task
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/inspections')}
                icon={<ClipboardCheck size={20} />}
                className="action-button"
              >
                New Inspection
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/users')}
                icon={<Users size={20} />}
                className="action-button"
              >
                Manage Users
              </Button>
              <Button
                variant="ghost"
                size="lg"
                onClick={() => navigate('/reports')}
                icon={<BarChart3 size={20} />}
                className="action-button"
              >
                View Reports
              </Button>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardHomeNew;
