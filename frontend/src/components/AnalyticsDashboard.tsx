import { useState } from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import { RefreshCw, Download } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [period, setPeriod] = useState('today');
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const exportData = () => {
    alert('Export functionality coming soon');
  };

  return (
    <ModernPageWrapper
      title="Analytics Dashboard"
      subtitle="Comprehensive insights and performance metrics"
      actions={
        <div className="flex items-center gap-3">
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

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={exportData}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      }
    >
      <div className="flex items-center justify-center h-96 border-2 border-dashed border-gray-300 rounded-lg">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Analytics Dashboard</h3>
          <p className="text-gray-500 dark:text-gray-400">This feature is currently under construction.</p>
        </div>
      </div>
    </ModernPageWrapper>
  );
};

export default AnalyticsDashboard;
