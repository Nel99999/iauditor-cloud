import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bell, Check, CheckCheck, Trash2, X } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Types
interface Notification {
  id: string;
  type: 'mention' | 'task_assigned' | 'workflow_approval' | 'inspection_completed' | string;
  title: string;
  message?: string;
  read: boolean;
  created_at: string;
  [key: string]: any;
}

interface NotificationStats {
  unread_count: number;
}

const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const fetchNotifications = async (): Promise<void> => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      const [notificationsRes, statsRes] = await Promise.all([
        axios.get<{ notifications: Notification[] }>(`${API_BASE_URL}/api/notifications?limit=10`, { headers }),
        axios.get<NotificationStats>(`${API_BASE_URL}/api/notifications/stats`, { headers })
      ]);

      setNotifications(notificationsRes.data.notifications || []);
      setUnreadCount(statsRes.data.unread_count || 0);
    } catch (err) {
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (notificationId: string): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.put(
        `${API_BASE_URL}/api/notifications/${notificationId}/read`,
        {},
        { headers }
      );

      // Update local state
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      ));
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(
        `${API_BASE_URL}/api/notifications/mark-all-read`,
        {},
        { headers }
      );

      // Update local state
      setNotifications(notifications.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const deleteNotification = async (notificationId: string): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.delete(
        `${API_BASE_URL}/api/notifications/${notificationId}`,
        { headers }
      );

      // Update local state
      setNotifications(notifications.filter(n => n.id !== notificationId));
      if (!notifications.find(n => n.id === notificationId)?.read) {
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
    } catch (err) {
      console.error('Error deleting notification:', err);
    }
  };

  const clearAll = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.delete(
        `${API_BASE_URL}/api/notifications/clear-all`,
        { headers }
      );

      setNotifications([]);
      setUnreadCount(0);
    } catch (err) {
      console.error('Error clearing notifications:', err);
    }
  };

  const getNotificationIcon = (type: string): JSX.Element => {
    const iconClass = "w-4 h-4";
    switch (type) {
      case 'mention':
        return <span className={`${iconClass} text-blue-500`}>@</span>;
      case 'task_assigned':
        return <Check className={`${iconClass} text-green-500`} />;
      case 'workflow_approval':
        return <CheckCheck className={`${iconClass} text-purple-500`} />;
      case 'inspection_completed':
        return <CheckCheck className={`${iconClass} text-green-500`} />;
      default:
        return <Bell className={`${iconClass} text-gray-500`} />;
    }
  };

  const getTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const time = new Date(timestamp);
    const seconds = Math.floor((now.getTime() - time.getTime()) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return time.toLocaleDateString();
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <button className="relative p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs bg-red-500">
              {unreadCount > 9 ? '9+' : unreadCount}
            </Badge>
          )}
        </button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-96 max-h-[600px] overflow-y-auto">
        <div className="flex items-center justify-between px-2 py-2">
          <DropdownMenuLabel className="text-base">Notifications</DropdownMenuLabel>
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1"
              >
                <CheckCheck className="w-3 h-3" />
                Mark all read
              </button>
            )}
            {notifications.length > 0 && (
              <button
                onClick={clearAll}
                className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 flex items-center gap-1"
              >
                <Trash2 className="w-3 h-3" />
                Clear all
              </button>
            )}
          </div>
        </div>
        
        <DropdownMenuSeparator />
        
        {loading && notifications.length === 0 ? (
          <div className="p-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Loading...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-8 text-center">
            <Bell className="w-12 h-12 text-gray-300 dark:text-gray-700 mx-auto mb-2" />
            <p className="text-sm text-gray-500 dark:text-gray-400">No notifications</p>
            <p className="text-xs text-gray-400 dark:text-gray-600 mt-1">
              You're all caught up!
            </p>
          </div>
        ) : (
          <div className="max-h-[400px] overflow-y-auto">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`px-3 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border-l-2 ${
                  notification.read
                    ? 'border-transparent bg-white dark:bg-gray-900'
                    : 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                }`}
                onClick={() => !notification.read && markAsRead(notification.id)}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {getNotificationIcon(notification.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm ${
                        notification.read
                          ? 'text-gray-600 dark:text-gray-400'
                          : 'text-gray-900 dark:text-white font-medium'
                      }`}>
                        {notification.title}
                      </p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        className="text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    
                    {notification.message && (
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 line-clamp-2">
                        {notification.message}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-gray-400 dark:text-gray-600">
                        {getTimeAgo(notification.created_at)}
                      </span>
                      {!notification.read && (
                        <Badge className="h-4 px-1.5 text-xs bg-blue-500">New</Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {notifications.length > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="justify-center text-sm text-blue-600 dark:text-blue-400 cursor-pointer">
              View all notifications
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default NotificationCenter;
