import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const SubtasksPanel = ({ taskId, onClose }) => {
  const { token } = useAuth();
  const [subtasks, setSubtasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSubtask, setNewSubtask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    assigned_to: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    if (taskId) {
      fetchSubtasks();
      fetchStats();
    }
  }, [taskId]);

  const fetchSubtasks = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/subtasks/${taskId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSubtasks(data);
      }
    } catch (error) {
      console.error('Error fetching subtasks:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/subtasks/${taskId}/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleAddSubtask = async () => {
    if (!newSubtask.title.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/subtasks/${taskId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSubtask)
      });

      if (response.ok) {
        setNewSubtask({ title: '', description: '', priority: 'medium', assigned_to: '' });
        setShowAddForm(false);
        fetchSubtasks();
        fetchStats();
      }
    } catch (error) {
      console.error('Error adding subtask:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (subtaskId, newStatus) => {
    try {
      const response = await fetch(`${backendUrl}/api/subtasks/${subtaskId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        fetchSubtasks();
        fetchStats();
      }
    } catch (error) {
      console.error('Error updating subtask:', error);
    }
  };

  const handleDeleteSubtask = async (subtaskId) => {
    if (!window.confirm('Are you sure you want to delete this subtask?')) return;

    try {
      const response = await fetch(`${backendUrl}/api/subtasks/${subtaskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchSubtasks();
        fetchStats();
      }
    } catch (error) {
      console.error('Error deleting subtask:', error);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
      urgent: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    };
    return colors[priority] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-gray-200 text-gray-800',
      in_progress: 'bg-blue-200 text-blue-800',
      completed: 'bg-green-200 text-green-800'
    };
    return colors[status] || colors.todo;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b dark:border-gray-700">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Subtasks</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {stats && (
            <div className="mt-4 grid grid-cols-4 gap-4">
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              </div>
              <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded">
                <p className="text-sm text-blue-600 dark:text-blue-400">To Do</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-200">{stats.todo}</p>
              </div>
              <div className="bg-yellow-100 dark:bg-yellow-900 p-3 rounded">
                <p className="text-sm text-yellow-600 dark:text-yellow-400">In Progress</p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-200">{stats.in_progress}</p>
              </div>
              <div className="bg-green-100 dark:bg-green-900 p-3 rounded">
                <p className="text-sm text-green-600 dark:text-green-400">Completed</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-200">{stats.completed}</p>
              </div>
            </div>
          )}

          {stats && stats.total > 0 && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                  {stats.completion_percentage.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${stats.completion_percentage}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 250px)' }}>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showAddForm ? 'Cancel' : '+ Add Subtask'}
          </button>

          {showAddForm && (
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <input
                type="text"
                value={newSubtask.title}
                onChange={(e) => setNewSubtask({ ...newSubtask, title: e.target.value })}
                placeholder="Subtask title"
                className="w-full px-4 py-2 mb-3 border rounded-lg dark:bg-gray-600 dark:border-gray-500 dark:text-white"
              />
              <textarea
                value={newSubtask.description}
                onChange={(e) => setNewSubtask({ ...newSubtask, description: e.target.value })}
                placeholder="Description (optional)"
                className="w-full px-4 py-2 mb-3 border rounded-lg dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                rows={2}
              />
              <select
                value={newSubtask.priority}
                onChange={(e) => setNewSubtask({ ...newSubtask, priority: e.target.value })}
                className="w-full px-4 py-2 mb-3 border rounded-lg dark:bg-gray-600 dark:border-gray-500 dark:text-white"
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
                <option value="urgent">Urgent</option>
              </select>
              <button
                onClick={handleAddSubtask}
                disabled={loading || !newSubtask.title.trim()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
              >
                {loading ? 'Adding...' : 'Add Subtask'}
              </button>
            </div>
          )}

          <div className="space-y-3">
            {subtasks.length === 0 ? (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <p className="text-lg">No subtasks yet</p>
                <p className="text-sm">Click "Add Subtask" to create one</p>
              </div>
            ) : (
              subtasks.map((subtask) => (
                <div
                  key={subtask.id}
                  className={`p-4 border rounded-lg ${
                    subtask.level > 1 ? 'ml-8 border-l-4 border-blue-400' : ''
                  } ${
                    subtask.status === 'completed' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-white dark:bg-gray-800'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className={`font-semibold ${
                          subtask.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'
                        }`}>
                          {subtask.title}
                        </h4>
                        <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(subtask.priority)}`}>
                          {subtask.priority}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(subtask.status)}`}>
                          {subtask.status.replace('_', ' ')}
                        </span>
                        {subtask.level > 1 && (
                          <span className="text-xs text-gray-500">Level {subtask.level}</span>
                        )}
                      </div>
                      {subtask.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{subtask.description}</p>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <select
                        value={subtask.status}
                        onChange={(e) => handleUpdateStatus(subtask.id, e.target.value)}
                        className="px-2 py-1 text-sm border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      >
                        <option value="todo">To Do</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                      </select>
                      <button
                        onClick={() => handleDeleteSubtask(subtask.id)}
                        className="px-2 py-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/20 rounded"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubtasksPanel;
