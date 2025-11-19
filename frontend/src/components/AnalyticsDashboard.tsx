import { ModernPageWrapper } from '@/design-system/components';

// ... existing imports ...

const AnalyticsDashboard = () => {
  // ... existing state ...

  // ... existing functions ...

  if (loading) {
    // ... existing loading ...
  }

  if (error) {
    // ... existing error ...
  }

  return (
    <ModernPageWrapper
      title="Analytics Dashboard"
      subtitle="Comprehensive insights and performance metrics"
      actions={
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
      }
    >
      <div className="space-y-6">
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
                {overview.metrics?.time_tracking?.total_hours?.toFixed(1) as any || 0}h
              </div>
              <div className="text-sm text-blue-600 mt-1">
                {overview.metrics?.time_tracking?.billable_hours?.toFixed(1) as any || 0}h billable
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
                  {tasksByStatus.map((_entry: any, index: number) => (
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
                      <td className="py-3 px-4 text-gray-900 dark:text-white">{user.hours_logged?.toFixed(1) as any || 0}h</td>
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
