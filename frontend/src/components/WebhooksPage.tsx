import { useState, useEffect } from 'react';
import axios from 'axios';
import { Webhook, Plus, Edit2, Trash2, X, Play, CheckCircle, XCircle, Clock } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const WebhooksPage = () => {
  const [webhooks, setWebhooks] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showLogsModal, setShowLogsModal] = useState<boolean>(false);
  const [selectedWebhook, setSelectedWebhook] = useState<any | null>(null);
  const [webhookLogs, setWebhookLogs] = useState<any[]>([]);
  const [testingWebhook, setTestingWebhook] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [],
    secret: '',
    active: true
  });

  const availableEvents = [
    'task.created',
    'task.updated',
    'task.completed',
    'inspection.completed',
    'checklist.completed',
    'workflow.approved',
    'workflow.rejected',
    'user.invited',
    'user.created'
  ];

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const fetchWebhooks = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`${API_BASE_URL}/api/webhooks`, { headers });
      setWebhooks(response.data.webhooks || []);
    } catch (err: unknown) {
      console.error('Error fetching webhooks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWebhook = async (e: any) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(`${API_BASE_URL}/api/webhooks`, formData, { headers });
      
      setShowCreateModal(false);
      setFormData({ name: '', url: '', events: [], secret: '', active: true });
      fetchWebhooks();
    } catch (err: unknown) {
      console.error('Error creating webhook:', err);
      alert((err as any).response?.data?.detail || 'Failed to create webhook');
    }
  };

  const handleUpdateWebhook = async (e: any) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.put(
        `${API_BASE_URL}/api/webhooks/${selectedWebhook.id}`,
        formData,
        { headers }
      );
      
      setShowEditModal(false);
      setSelectedWebhook(null);
      setFormData({ name: '', url: '', events: [], secret: '', active: true });
      fetchWebhooks();
    } catch (err: unknown) {
      console.error('Error updating webhook:', err);
      alert((err as any).response?.data?.detail || 'Failed to update webhook');
    }
  };

  const handleDeleteWebhook = async (webhookId: string) => {
    if (!window.confirm('Are you sure you want to delete this webhook?')) return;
    
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API_BASE_URL}/api/webhooks/${webhookId}`, { headers });
      fetchWebhooks();
    } catch (err: unknown) {
      console.error('Error deleting webhook:', err);
      alert((err as any).response?.data?.detail || 'Failed to delete webhook');
    }
  };

  const handleTestWebhook = async (webhookId: string) => {
    try {
      setTestingWebhook(webhookId);
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(
        `${API_BASE_URL}/api/webhooks/${webhookId}/test`,
        {},
        { headers }
      );
      
      alert('Test webhook sent successfully!');
    } catch (err: unknown) {
      console.error('Error testing webhook:', err);
      alert((err as any).response?.data?.detail || 'Failed to test webhook');
    } finally {
      setTestingWebhook(null);
    }
  };

  const handleToggleActive = async (webhook: any) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.put(
        `${API_BASE_URL}/api/webhooks/${webhook.id}`,
        { ...webhook, active: !webhook.active },
        { headers }
      );
      
      fetchWebhooks();
    } catch (err: unknown) {
      console.error('Error toggling webhook:', err);
      alert((err as any).response?.data?.detail || 'Failed to toggle webhook');
    }
  };

  const openEditModal = (webhook: any) => {
    setSelectedWebhook(webhook);
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events || [],
      secret: webhook.secret || '',
      active: webhook.active
    });
    setShowEditModal(true);
  };

  const openLogsModal = async (webhook: any) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(
        `${API_BASE_URL}/api/webhooks/${webhook.id}/logs`,
        { headers }
      );
      
      setWebhookLogs(response.data.logs || []);
      setSelectedWebhook(webhook);
      setShowLogsModal(true);
    } catch (err: unknown) {
      console.error('Error fetching webhook logs:', err);
      alert((err as any).response?.data?.detail || 'Failed to fetch webhook logs');
    }
  };

  const toggleEvent = (event: any) => {
    if (formData.events.includes(event)) {
      setFormData({
        ...formData,
        events: formData.events.filter((e: any) => e !== event)
      });
    } else {
      setFormData({
        ...formData,
        events: [...formData.events, event]
      });
    }
  };

  const getStatusColor = (status: any) => {
    switch (status) {
      case 'success':
        return 'text-green-600 dark:text-green-400';
      case 'failed':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Webhook className="w-8 h-8 text-blue-600" />
              Webhooks
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Configure webhooks to receive real-time event notifications
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Webhook
          </button>
        </div>

        {/* Webhooks List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : webhooks.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-12 text-center border border-gray-200 dark:border-gray-700">
            <Webhook className="w-16 h-16 text-gray-300 dark:text-gray-700 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No webhooks configured yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {webhooks.map((webhook: any) => (
              <div
                key={webhook.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {webhook.name}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          webhook.active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
                        }`}
                      >
                        {webhook.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 break-all">
                      {webhook.url}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleActive(webhook)}
                      className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                      title={webhook.active ? 'Deactivate' : 'Activate'}
                    >
                      {webhook.active ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => handleTestWebhook(webhook.id)}
                      disabled={testingWebhook === webhook.id}
                      className="p-2 text-gray-600 hover:text-green-600 dark:text-gray-400 dark:hover:text-green-400 disabled:opacity-50"
                      title="Test Webhook"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openEditModal(webhook)}
                      className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteWebhook(webhook.id)}
                      className="p-2 text-gray-600 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                  <span>{webhook.events?.length || 0} events subscribed</span>
                  <span>•</span>
                  <span>{webhook.delivery_count || 0} deliveries</span>
                  {webhook.last_delivery && (
                    <>
                      <span>•</span>
                      <span>Last: {new Date(webhook.last_delivery).toLocaleDateString()}</span>
                    </>
                  )}
                </div>

                <div className="flex flex-wrap gap-2">
                  {webhook.events && webhook.events.map((event: string) => (
                    <span
                      key={event}
                      className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded text-xs"
                    >
                      {event}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => openLogsModal(webhook)}
                  className="mt-4 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  View Delivery Logs
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Create Webhook Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Create Webhook</h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setFormData({ name: '', url: '', events: [], secret: '', active: true });
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateWebhook} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Webhook Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                    placeholder="My Webhook"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Webhook URL *
                  </label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                    placeholder="https://example.com/webhook"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Secret (optional)
                  </label>
                  <input
                    type="text"
                    value={formData.secret}
                    onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                    placeholder="webhook_secret_key"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Used to sign webhook payloads for verification
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Events to Subscribe *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {availableEvents.map((event: string) => (
                      <label
                        key={event}
                        className="flex items-center gap-2 p-3 border border-gray-300 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900"
                      >
                        <input
                          type="checkbox"
                          checked={formData.events.includes(event)}
                          onChange={() => toggleEvent(event)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900 dark:text-white">{event}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="active"
                    checked={formData.active}
                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <label htmlFor="active" className="text-sm text-gray-700 dark:text-gray-300">
                    Active (start receiving events immediately)
                  </label>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setFormData({ name: '', url: '', events: [], secret: '', active: true });
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={formData.events.length === 0}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Create Webhook
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal - Similar to Create but with update handler */}
        {showEditModal && selectedWebhook && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Edit Webhook</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedWebhook(null);
                    setFormData({ name: '', url: '', events: [], secret: '', active: true });
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleUpdateWebhook} className="p-6 space-y-4">
                {/* Same form fields as create modal */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Webhook Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Webhook URL *
                  </label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Secret (optional)
                  </label>
                  <input
                    type="text"
                    value={formData.secret}
                    onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Events to Subscribe *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {availableEvents.map((event: string) => (
                      <label
                        key={event}
                        className="flex items-center gap-2 p-3 border border-gray-300 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900"
                      >
                        <input
                          type="checkbox"
                          checked={formData.events.includes(event)}
                          onChange={() => toggleEvent(event)}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-900 dark:text-white">{event}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedWebhook(null);
                      setFormData({ name: '', url: '', events: [], secret: '', active: true });
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Update Webhook
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Logs Modal */}
        {showLogsModal && selectedWebhook && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Webhook Delivery Logs
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {selectedWebhook.name}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowLogsModal(false);
                    setSelectedWebhook(null);
                    setWebhookLogs([]);
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                {webhookLogs.length === 0 ? (
                  <div className="text-center py-12">
                    <Clock className="w-12 h-12 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                    <p className="text-gray-500 dark:text-gray-400">No delivery logs yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {webhookLogs.map((log) => (
                      <div
                        key={log.id}
                        className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className={getStatusColor(log.status)}>
                              {log.status === 'success' ? (
                                <CheckCircle className="w-5 h-5" />
                              ) : (
                                <XCircle className="w-5 h-5" />
                              )}
                            </span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                              {log.event}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(log.timestamp).toLocaleString()}
                          </span>
                        </div>
                        
                        <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                          <p>Status Code: {log.status_code}</p>
                          {log.response_time && <p>Response Time: {log.response_time}ms</p>}
                          {log.error && (
                            <p className="text-red-600 dark:text-red-400">Error: {log.error}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WebhooksPage;
