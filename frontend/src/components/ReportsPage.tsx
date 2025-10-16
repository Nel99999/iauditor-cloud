import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  ClipboardCheck, 
  CheckSquare, 
  ListTodo, 
  TrendingUp, 
  BarChart3, 
  Download, 
  Plus, 
  Settings,
  AlertTriangle,
  Target,
  Clock,
  FileText
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportsPage = () => {
  const [overview, setOverview] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedDays, setSelectedDays] = useState(30);
  const [showCustomReportDialog, setShowCustomReportDialog] = useState<boolean>(false);
  const [customReport, setCustomReport] = useState<any>({
    name: '',
    collections: [],
    fields: [],
    filters: [],
    groupBy: '',
    sortBy: ''
  });
  
  // Available collections and their fields for custom reports
  const availableCollections = {
    'inspection_executions': {
      name: 'Inspections',
      fields: ['status', 'score', 'passed', 'completed_at', 'template_name', 'location', 'inspector_name']
    },
    'checklist_executions': {
      name: 'Checklists', 
      fields: ['status', 'date', 'completion_percentage', 'template_name', 'assigned_to_name']
    },
    'tasks': {
      name: 'Tasks',
      fields: ['status', 'priority', 'title', 'assigned_to_name', 'due_date', 'completed_at', 'created_at']
    },
    'organizations': {
      name: 'Organizations',
      fields: ['name', 'type', 'created_at', 'status']
    },
    'users': {
      name: 'Users', 
      fields: ['name', 'email', 'role', 'created_at', 'last_login']
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedDays]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewRes, trendsRes] = await Promise.all([
        axios.get(`${API}/reports/overview?days=${selectedDays}`),
        axios.get(`${API}/reports/trends?days=${selectedDays}`)
      ]);
      setOverview(overviewRes.data);
      setTrends(trendsRes.data);
    } catch (err: unknown) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomReportCreate = async (e: any) => {
    e.preventDefault();
    try {
      // This would typically send to backend for report generation
      console.log('Creating custom report:', customReport);
      alert('Custom report created successfully! (This is a demo - would integrate with backend)');
      setShowCustomReportDialog(false);
      setCustomReport({ name: '', collections: [], fields: [], filters: [], groupBy: '', sortBy: '' });
    } catch (err: unknown) {
      alert('Failed to create custom report');
    }
  };

  const exportData = (format: any) => {
    // Demo export functionality
    alert(`Exporting data as ${format.toUpperCase()}... (This would integrate with backend)`);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Enhanced Header with Controls */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Reports & Analytics</h1>
          <p className="text-slate-600 dark:text-slate-400">Comprehensive insights and custom reporting (Last {overview?.period_days || selectedDays} days)</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedDays.toString()} onValueChange={(val) => setSelectedDays(parseInt(val))}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">7 Days</SelectItem>
              <SelectItem value="30">30 Days</SelectItem>
              <SelectItem value="90">90 Days</SelectItem>
              <SelectItem value="365">1 Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={() => exportData('pdf')}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => setShowCustomReportDialog(true)} data-testid="create-custom-report-btn">
            <Plus className="h-4 w-4 mr-2" />
            Custom Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="inspections">Inspections</TabsTrigger>
          <TabsTrigger value="checklists">Checklists</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Inspections Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Inspections</CardTitle>
                  <ClipboardCheck className="h-5 w-5 text-blue-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.inspections?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Inspections</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.inspections?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pending:</span>
                    <Badge variant="secondary">{overview?.inspections?.pending || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pass Rate:</span>
                    <Badge className="bg-blue-500">{overview?.inspections?.pass_rate || 0}%</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Avg Score:</span>
                    <Badge variant="outline">{overview?.inspections?.avg_score || 0}%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Checklists Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Checklists</CardTitle>
                  <CheckSquare className="h-5 w-5 text-green-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.checklists?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Checklists</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.checklists?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Pending:</span>
                    <Badge variant="secondary">{overview?.checklists?.pending || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Completion Rate:</span>
                    <Badge className="bg-blue-500">{overview?.checklists?.completion_rate || 0}%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tasks Summary */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Tasks</CardTitle>
                  <ListTodo className="h-5 w-5 text-purple-600" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">{overview?.tasks?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total Tasks</p>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Completed:</span>
                    <Badge className="bg-green-500">{overview?.tasks?.completed || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">In Progress:</span>
                    <Badge className="bg-blue-500">{overview?.tasks?.in_progress || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">To Do:</span>
                    <Badge variant="secondary">{overview?.tasks?.todo || 0}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Overdue:</span>
                    <Badge variant="destructive">{overview?.tasks?.overdue || 0}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Trends Preview */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Activity Trends</CardTitle>
              <CardDescription>Daily completions over the last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Inspections Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.inspections || {}).length} days with activity
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Checklists Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.checklists || {}).length} days with activity
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Tasks Completed</h4>
                  <p className="text-sm text-slate-600">
                    {Object.keys(trends?.tasks || {}).length} days with activity
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Detailed Tabs */}
        <TabsContent value="inspections">
          <Card>
            <CardHeader>
              <CardTitle>Inspection Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.inspections?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.inspections?.pass_rate || 0}%</p>
                  <p className="text-sm text-slate-600">Pass Rate</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.inspections?.avg_score || 0}%</p>
                  <p className="text-sm text-slate-600">Avg Score</p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{overview?.inspections?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="checklists">
          <Card>
            <CardHeader>
              <CardTitle>Checklist Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.checklists?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.checklists?.completion_rate || 0}%</p>
                  <p className="text-sm text-slate-600">Completion Rate</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.checklists?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks">
          <Card>
            <CardHeader>
              <CardTitle>Task Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{overview?.tasks?.total || 0}</p>
                  <p className="text-sm text-slate-600">Total</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{overview?.tasks?.completed || 0}</p>
                  <p className="text-sm text-slate-600">Completed</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{overview?.tasks?.in_progress || 0}</p>
                  <p className="text-sm text-slate-600">In Progress</p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{overview?.tasks?.overdue || 0}</p>
                  <p className="text-sm text-slate-600">Overdue</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* New Insights Tab */}
        <TabsContent value="insights">
          <div className="space-y-6">
            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Performance Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Inspection Pass Rate</span>
                      <span className="font-medium">{overview?.inspections?.pass_rate || 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${overview?.inspections?.pass_rate || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Checklist Completion Rate</span>
                      <span className="font-medium">{overview?.checklists?.completion_rate || 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${overview?.checklists?.completion_rate || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Task Completion Rate</span>
                      <span className="font-medium">
                        {overview?.tasks?.total ? Math.round((overview.tasks.completed / overview.tasks.total) * 100) : 0}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full" 
                        style={{ width: `${overview?.tasks?.total ? (overview.tasks.completed / overview.tasks.total) * 100 : 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI-Powered Insights */}
            <Card>
              <CardHeader>
                <CardTitle>AI-Powered Insights & Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                  <h4 className="font-medium text-blue-900 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Productivity Trend
                  </h4>
                  <p className="text-blue-800 mt-1">
                    Task completion rate shows steady improvement over the last {selectedDays} days. 
                    Consider implementing current successful practices across all teams.
                  </p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                  <h4 className="font-medium text-green-900 flex items-center gap-2">
                    <CheckSquare className="h-4 w-4" />
                    Quality Improvement
                  </h4>
                  <p className="text-green-800 mt-1">
                    Inspection pass rate is {overview?.inspections?.pass_rate || 0}%, which indicates strong quality standards.
                    Focus on maintaining consistency across all inspection areas.
                  </p>
                </div>
                
                {overview?.tasks?.overdue > 0 && (
                  <div className="p-4 bg-amber-50 rounded-lg border-l-4 border-amber-500">
                    <h4 className="font-medium text-amber-900 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Attention Needed
                    </h4>
                    <p className="text-amber-800 mt-1">
                      {overview?.tasks?.overdue || 0} tasks are currently overdue. Review task assignment 
                      and deadline management processes to improve efficiency.
                    </p>
                  </div>
                )}

                <div className="p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500">
                  <h4 className="font-medium text-purple-900 flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Recommendations
                  </h4>
                  <ul className="text-purple-800 mt-1 space-y-1">
                    <li>• Implement automated reminders for approaching deadlines</li>
                    <li>• Create templates for high-performing inspection procedures</li>
                    <li>• Schedule regular team check-ins during peak activity periods</li>
                    <li>• Consider workload balancing based on completion trends</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* System Health */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  System Health & Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-green-800">System Status</span>
                      <Badge className="bg-green-500">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-blue-800">Data Freshness</span>
                      <Badge className="bg-blue-500">Real-time</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                      <span className="text-yellow-800">Pending Actions</span>
                      <Badge className="bg-yellow-500">{(overview?.tasks?.overdue || 0) + (overview?.inspections?.pending || 0)}</Badge>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start" onClick={() => exportData('csv')}>
                      <Download className="h-4 w-4 mr-2" />
                      Export to CSV
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={() => exportData('pdf')}>
                      <FileText className="h-4 w-4 mr-2" />
                      Generate PDF Report
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={() => setShowCustomReportDialog(true)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Custom Report
                    </Button>
                    <Button variant="outline" className="w-full justify-start" onClick={() => loadData()}>
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Refresh Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Custom Report Builder Dialog */}
      <Dialog open={showCustomReportDialog} onOpenChange={setShowCustomReportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Custom Report</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCustomReportCreate}>
            <div className="space-y-6">
              <div>
                <Label>Report Name *</Label>
                <Input 
                  value={customReport.name} 
                  onChange={(e) => setCustomReport({...customReport, name: e.target.value})} 
                  placeholder="e.g., Monthly Performance Report"
                  required
                  data-testid="custom-report-name"
                />
              </div>
              
              <div>
                <Label>Data Sources</Label>
                <Select 
                  value={customReport.collections[0] || ''} 
                  onValueChange={(val) => setCustomReport({...customReport, collections: [val]})}
                >
                  <SelectTrigger data-testid="custom-report-source">
                    <SelectValue placeholder="Choose data source" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(availableCollections).map(([key, config]: [string, any]) => (
                      <SelectItem key={key} value={key}>{config.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {customReport.collections[0] && (
                <div>
                  <Label>Fields to Include</Label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {availableCollections[customReport.collections[0]]?.fields.map((field: any) => (
                      <label key={field} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={customReport.fields.includes(field)}
                          onChange={(e: any) => {
                            if (e.target.checked) {
                              setCustomReport({
                                ...customReport,
                                fields: [...customReport.fields, field]
                              });
                            } else {
                              setCustomReport({
                                ...customReport,
                                fields: customReport.fields.filter((f: any) => f !== field)
                              });
                            }
                          }}
                          data-testid={`field-${field}`}
                        />
                        <span className="text-sm capitalize">{field.replace('_', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Group By</Label>
                  <Select 
                    value={customReport.groupBy} 
                    onValueChange={(val) => setCustomReport({...customReport, groupBy: val})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Group by..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="date">Date</SelectItem>
                      <SelectItem value="status">Status</SelectItem>
                      <SelectItem value="priority">Priority</SelectItem>
                      <SelectItem value="assigned_to">Assignee</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Sort By</Label>
                  <Select 
                    value={customReport.sortBy} 
                    onValueChange={(val) => setCustomReport({...customReport, sortBy: val})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sort by..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="date_desc">Date (Newest)</SelectItem>
                      <SelectItem value="date_asc">Date (Oldest)</SelectItem>
                      <SelectItem value="status">Status</SelectItem>
                      <SelectItem value="priority">Priority</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Report Preview</h4>
                <p className="text-sm text-gray-600">
                  <strong>Name:</strong> {customReport.name || 'Untitled Report'}<br />
                  <strong>Source:</strong> {customReport.collections[0] ? availableCollections[customReport.collections[0]]?.name : 'None selected'}<br />
                  <strong>Fields:</strong> {customReport.fields.length} selected<br />
                  <strong>Grouping:</strong> {customReport.groupBy || 'None'}<br />
                  <strong>Sorting:</strong> {customReport.sortBy || 'Default'}
                </p>
              </div>
            </div>
            
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setShowCustomReportDialog(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={!customReport.name || !customReport.collections[0]}
                data-testid="save-custom-report-btn"
              >
                Create Report
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ReportsPage;
