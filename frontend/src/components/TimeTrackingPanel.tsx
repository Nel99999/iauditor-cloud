import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Play, Square, Plus, Trash2, DollarSign } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Types
interface TimeEntry {
  id: string;
  task_id: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  description?: string;
  is_billable: boolean;
  [key: string]: any;
}

interface ManualEntryData {
  hours: string;
  minutes: string;
  description: string;
  is_billable: boolean;
}

interface TimeTrackingPanelProps {
  taskId: string;
  taskTitle: string;
}

const TimeTrackingPanel: React.FC<TimeTrackingPanelProps> = ({ taskId }) => {
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>([]);
  const [activeTimer, setActiveTimer] = useState<TimeEntry | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [showManualEntry, setShowManualEntry] = useState<boolean>(false);
  const [manualEntryData, setManualEntryData] = useState<ManualEntryData>({
    hours: '',
    minutes: '',
    description: '',
    is_billable: false
  });

  useEffect(() => {
    if (taskId) {
      fetchTimeEntries();
      checkActiveTimer();
    }
  }, [taskId]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (activeTimer) {
      interval = setInterval(() => {
        const start = new Date(activeTimer.start_time);
        const now = new Date();
        const diff = Math.floor((now.getTime() - start.getTime()) / 1000);
        setElapsedTime(diff);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeTimer]);

  const fetchTimeEntries = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get<{ entries: TimeEntry[] }>(
        `${API_BASE_URL}/api/time-tracking/entries?task_id=${taskId}`,
        { headers }
      );
      setTimeEntries(response.data.entries || []);
    } catch (err) {
      console.error('Error fetching time entries:', err);
    }
  };

  const checkActiveTimer = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get<{ entry: TimeEntry }>(
        `${API_BASE_URL}/api/time-tracking/active`,
        { headers }
      );
      
      if (response.data.entry && response.data.entry.task_id === taskId) {
        setActiveTimer(response.data.entry);
      }
    } catch (err) {
      // No active timer
    }
  };

  const handleStartTimer = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.post<{ entry: TimeEntry }>(
        `${API_BASE_URL}/api/time-tracking/start`,
        { task_id: taskId },
        { headers }
      );
      
      setActiveTimer(response.data.entry);
    } catch (err: any) {
      console.error('Error starting timer:', err);
      alert(err.response?.data?.detail || 'Failed to start timer');
    }
  };

  const handleStopTimer = async (): Promise<void> => {
    if (!activeTimer) return;
    
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(
        `${API_BASE_URL}/api/time-tracking/${activeTimer.id}/stop`,
        {},
        { headers }
      );
      
      setActiveTimer(null);
      setElapsedTime(0);
      fetchTimeEntries();
    } catch (err: any) {
      console.error('Error stopping timer:', err);
      alert(err.response?.data?.detail || 'Failed to stop timer');
    }
  };

  const handleManualEntry = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const totalMinutes = parseInt(manualEntryData.hours || '0') * 60 + parseInt(manualEntryData.minutes || '0');
      
      await axios.post(
        `${API_BASE_URL}/api/time-tracking/manual`,
        {
          task_id: taskId,
          duration_minutes: totalMinutes,
          description: manualEntryData.description,
          is_billable: manualEntryData.is_billable
        },
        { headers }
      );
      
      setShowManualEntry(false);
      setManualEntryData({ hours: '', minutes: '', description: '', is_billable: false });
      fetchTimeEntries();
    } catch (err: any) {
      console.error('Error creating manual entry:', err);
      alert(err.response?.data?.detail || 'Failed to create time entry');
    }
  };

  const handleDeleteEntry = async (entryId: string): Promise<void> => {
    if (!window.confirm('Delete this time entry?')) return;
    
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(
        `${API_BASE_URL}/api/time-tracking/entries/${entryId}`,
        { headers }
      );
      
      fetchTimeEntries();
    } catch (err: any) {
      console.error('Error deleting entry:', err);
      alert(err.response?.data?.detail || 'Failed to delete entry');
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const totalTime = timeEntries.reduce((sum, entry) => sum + (entry.duration_minutes || 0), 0);
  const billableTime = timeEntries.filter((e: any) => e.is_billable).reduce((sum, entry) => sum + (entry.duration_minutes || 0), 0);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-600" />
          Time Tracking
        </h3>
        <button
          onClick={() => setShowManualEntry(!showManualEntry)}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          Manual Entry
        </button>
      </div>

      {/* Timer Widget */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
        <div className="text-center mb-4">
          <div className="text-4xl font-mono font-bold text-gray-900 dark:text-white">
            {formatTime(elapsedTime)}
          </div>
          {activeTimer && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Recording time...
            </p>
          )}
        </div>
        
        <div className="flex gap-2">
          {!activeTimer ? (
            <button
              onClick={handleStartTimer}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4" />
              Start Timer
            </button>
          ) : (
            <button
              onClick={handleStopTimer}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center justify-center gap-2"
            >
              <Square className="w-4 h-4" />
              Stop Timer
            </button>
          )}
        </div>
      </div>

      {/* Manual Entry Form */}
      {showManualEntry && (
        <form onSubmit={handleManualEntry} className="mb-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Hours
              </label>
              <input
                type="number"
                min="0"
                value={manualEntryData.hours}
                onChange={(e) => setManualEntryData({ ...manualEntryData, hours: e.target.value })}
                className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-sm"
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Minutes
              </label>
              <input
                type="number"
                min="0"
                max="59"
                value={manualEntryData.minutes}
                onChange={(e) => setManualEntryData({ ...manualEntryData, minutes: e.target.value })}
                className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-sm"
                placeholder="0"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description (optional)
            </label>
            <input
              type="text"
              value={manualEntryData.description}
              onChange={(e) => setManualEntryData({ ...manualEntryData, description: e.target.value })}
              className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-sm"
              placeholder="What did you work on?"
            />
          </div>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={manualEntryData.is_billable}
              onChange={(e) => setManualEntryData({ ...manualEntryData, is_billable: e.target.checked })}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-1">
              <DollarSign className="w-3 h-3" />
              Billable
            </span>
          </label>
          
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setShowManualEntry(false);
                setManualEntryData({ hours: '', minutes: '', description: '', is_billable: false });
              }}
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
            >
              Add Entry
            </button>
          </div>
        </form>
      )}

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Total Time</div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {formatDuration(totalTime)}
          </div>
        </div>
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-xs text-green-600 dark:text-green-400 mb-1 flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            Billable Time
          </div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {formatDuration(billableTime)}
          </div>
        </div>
      </div>

      {/* Time Entries List */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          Time Entries ({timeEntries.length})
        </h4>
        
        {timeEntries.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-6">
            No time entries yet. Start the timer or add a manual entry.
          </p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {timeEntries.map((entry) => (
              <div
                key={entry.id}
                className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {formatDuration(entry.duration_minutes)}
                    </span>
                    {entry.is_billable && (
                      <span className="px-2 py-0.5 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded text-xs flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        Billable
                      </span>
                    )}
                  </div>
                  {entry.description && (
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {entry.description}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {new Date(entry.start_time).toLocaleDateString()} at{' '}
                    {new Date(entry.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                
                <button
                  onClick={() => handleDeleteEntry(entry.id)}
                  className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeTrackingPanel;
