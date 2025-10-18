// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Plus, Trash2, GripVertical, Save, ArrowLeft, Image, FileSignature,
  Settings, Calendar, BarChart3, Link as LinkIcon, AlertTriangle, Clock, Users
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QUESTION_TYPES = [
  { value: 'text', label: 'Text Input' },
  { value: 'number', label: 'Number Input' },
  { value: 'yes_no', label: 'Yes/No' },
  { value: 'multiple_choice', label: 'Multiple Choice' },
  { value: 'photo', label: 'Photo Capture' },
  { value: 'signature', label: 'Signature' },
];

const EnhancedTemplateBuilderPage = () => {
  const navigate = useNavigate();
  const { templateId } = useParams();
  const isEdit = !!templateId;

  const [template, setTemplate] = useState({
    name: '',
    description: '',
    category: 'safety',
    scoring_enabled: false,
    pass_percentage: 80,
    require_gps: false,
    require_photos: false,
    // V1 Enhancement fields
    unit_ids: [],
    asset_type_ids: [],
    recurrence_rule: null,
    auto_assign_logic: null,
    assigned_inspector_ids: [],
    requires_competency: null,
    estimated_duration_minutes: null,
    auto_create_work_order_on_fail: false,
    work_order_priority: 'normal',
    questions: [],
  });
  
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');

  useEffect(() => {
    loadUnits();
    if (isEdit) {
      loadTemplate();
    }
  }, [templateId]);

  const loadUnits = async () => {
    try {
      const response = await axios.get(`${API}/organizations/units`);
      setUnits(response.data);
    } catch (err) {
      console.error('Failed to load units:', err);
    }
  };

  const loadTemplate = async () => {
    try {
      const response = await axios.get(`${API}/inspections/templates/${templateId}`);
      setTemplate(response.data);
    } catch (err) {
      console.error('Failed to load template:', err);
      alert('Failed to load template');
      navigate('/inspections');
    }
  };

  const handleAddQuestion = () => {
    setTemplate({
      ...template,
      questions: [
        ...template.questions,
        {
          question_text: '',
          question_type: 'text',
          required: true,
          options: [],
          scoring_enabled: template.scoring_enabled,
          pass_score: null,
          order: template.questions.length,
          // V1 Enhancement fields
          photo_required: false,
          min_photos: 0,
          max_photos: 10,
          signature_required: false,
          conditional_logic: null,
          help_text: '',
        },
      ],
    });
  };

  const handleRemoveQuestion = (index) => {
    setTemplate({
      ...template,
      questions: template.questions.filter((_, i) => i !== index),
    });
  };

  const handleQuestionChange = (index, field, value) => {
    const newQuestions = [...template.questions];
    newQuestions[index] = { ...newQuestions[index], [field]: value };
    setTemplate({ ...template, questions: newQuestions });
  };

  const handleSave = async () => {
    if (!template.name.trim()) {
      alert('Please enter a template name');
      return;
    }

    if (template.questions.length === 0) {
      alert('Please add at least one question');
      return;
    }

    try {
      setLoading(true);
      if (isEdit) {
        await axios.put(`${API}/inspections/templates/${templateId}`, template);
      } else {
        await axios.post(`${API}/inspections/templates`, template);
      }
      navigate('/inspections');
    } catch (err) {
      console.error('Failed to save template:', err);
      alert('Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper 
      title={isEdit ? 'Edit Template' : 'Enhanced Template Builder'} 
      subtitle={isEdit ? 'Update inspection template with V1 features' : 'Build advanced inspection templates'}
      actions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/inspections')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Saving...' : 'Save Template'}
          </Button>
        </div>
      }
    >
      <div className="space-y-6 max-w-5xl">

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="basic">
            <Settings className="h-4 w-4 mr-2" />
            Basic Info
          </TabsTrigger>
          <TabsTrigger value="questions">
            <FileSignature className="h-4 w-4 mr-2" />
            Questions
          </TabsTrigger>
          <TabsTrigger value="scheduling">
            <Calendar className="h-4 w-4 mr-2" />
            Scheduling
          </TabsTrigger>
          <TabsTrigger value="workflow">
            <AlertTriangle className="h-4 w-4 mr-2" />
            Workflow
          </TabsTrigger>
          <TabsTrigger value="advanced">
            <BarChart3 className="h-4 w-4 mr-2" />
            Advanced
          </TabsTrigger>
        </TabsList>

        {/* TAB 1: Basic Information */}
        <TabsContent value="basic">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>Template details and settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Template Name *</Label>
                <Input
                  id="name"
                  value={template.name}
                  onChange={(e) => setTemplate({ ...template, name: e.target.value })}
                  placeholder="e.g., Monthly Safety Inspection"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={template.description}
                  onChange={(e) => setTemplate({ ...template, description: e.target.value })}
                  placeholder="Describe what this inspection covers..."
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select
                    value={template.category}
                    onValueChange={(value) => setTemplate({ ...template, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="safety">Safety</SelectItem>
                      <SelectItem value="quality">Quality</SelectItem>
                      <SelectItem value="maintenance">Maintenance</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="environmental">Environmental</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="estimated_duration">Estimated Duration (minutes)</Label>
                  <Input
                    id="estimated_duration"
                    type="number"
                    min="1"
                    value={template.estimated_duration_minutes || ''}
                    onChange={(e) => setTemplate({ ...template, estimated_duration_minutes: parseInt(e.target.value) || null })}
                    placeholder="e.g., 30"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Scoring Enabled</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable pass/fail scoring for this inspection
                    </p>
                  </div>
                  <Switch
                    checked={template.scoring_enabled}
                    onCheckedChange={(checked) => setTemplate({ ...template, scoring_enabled: checked })}
                  />
                </div>

                {template.scoring_enabled && (
                  <div className="space-y-2">
                    <Label htmlFor="pass_percentage">Pass Percentage (%)</Label>
                    <Input
                      id="pass_percentage"
                      type="number"
                      min="0"
                      max="100"
                      value={template.pass_percentage}
                      onChange={(e) => setTemplate({ ...template, pass_percentage: parseFloat(e.target.value) })}
                    />
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Require GPS Location</Label>
                    <p className="text-sm text-muted-foreground">
                      Capture location when starting inspection
                    </p>
                  </div>
                  <Switch
                    checked={template.require_gps}
                    onCheckedChange={(checked) => setTemplate({ ...template, require_gps: checked })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Require Photos</Label>
                    <p className="text-sm text-muted-foreground">
                      General photo requirement for inspection
                    </p>
                  </div>
                  <Switch
                    checked={template.require_photos}
                    onCheckedChange={(checked) => setTemplate({ ...template, require_photos: checked })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 2: Questions */}
        <TabsContent value="questions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Inspection Questions</CardTitle>
                  <CardDescription>
                    Configure questions with photo, signature, and conditional logic
                  </CardDescription>
                </div>
                <Button onClick={handleAddQuestion} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Question
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {template.questions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileSignature className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No questions added yet</p>
                  <p className="text-sm">Click "Add Question" to get started</p>
                </div>
              ) : (
                template.questions.map((question, index) => (
                  <Card key={index} className="border-l-4 border-l-primary/30">
                    <CardContent className="pt-6 space-y-4">
                      <div className="flex items-start justify-between gap-4">
                        <Badge variant="outline" className="mt-1">Q{index + 1}</Badge>
                        <div className="flex-1 space-y-4">
                          <div className="space-y-2">
                            <Label>Question Text *</Label>
                            <Input
                              value={question.question_text}
                              onChange={(e) => handleQuestionChange(index, 'question_text', e.target.value)}
                              placeholder="Enter your question..."
                            />
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label>Question Type</Label>
                              <Select
                                value={question.question_type}
                                onValueChange={(value) => handleQuestionChange(index, 'question_type', value)}
                              >
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  {QUESTION_TYPES.map(type => (
                                    <SelectItem key={type.value} value={type.value}>
                                      {type.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>

                            {question.question_type === 'multiple_choice' && (
                              <div className="space-y-2">
                                <Label>Options (comma-separated)</Label>
                                <Input
                                  value={question.options?.join(', ') || ''}
                                  onChange={(e) => handleQuestionChange(index, 'options', e.target.value.split(',').map(o => o.trim()))}
                                  placeholder="Yes, No, N/A"
                                />
                              </div>
                            )}
                          </div>

                          {/* V1 Enhancement: Photo Requirements */}
                          <div className="space-y-3 bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Image className="h-4 w-4 text-primary" />
                                <Label>Photo Required</Label>
                              </div>
                              <Switch
                                checked={question.photo_required}
                                onCheckedChange={(checked) => handleQuestionChange(index, 'photo_required', checked)}
                              />
                            </div>

                            {question.photo_required && (
                              <div className="grid grid-cols-2 gap-4 mt-2">
                                <div className="space-y-2">
                                  <Label className="text-sm">Min Photos</Label>
                                  <Input
                                    type="number"
                                    min="0"
                                    max={question.max_photos || 10}
                                    value={question.min_photos || 0}
                                    onChange={(e) => handleQuestionChange(index, 'min_photos', parseInt(e.target.value) || 0)}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label className="text-sm">Max Photos</Label>
                                  <Input
                                    type="number"
                                    min={question.min_photos || 0}
                                    max="20"
                                    value={question.max_photos || 10}
                                    onChange={(e) => handleQuestionChange(index, 'max_photos', parseInt(e.target.value) || 10)}
                                  />
                                </div>
                              </div>
                            )}
                          </div>

                          {/* V1 Enhancement: Signature Required */}
                          <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                            <div className="flex items-center gap-2">
                              <FileSignature className="h-4 w-4 text-primary" />
                              <Label>Signature Required</Label>
                            </div>
                            <Switch
                              checked={question.signature_required}
                              onCheckedChange={(checked) => handleQuestionChange(index, 'signature_required', checked)}
                            />
                          </div>

                          {/* V1 Enhancement: Help Text */}
                          <div className="space-y-2">
                            <Label>Help Text (optional)</Label>
                            <Textarea
                              value={question.help_text || ''}
                              onChange={(e) => handleQuestionChange(index, 'help_text', e.target.value)}
                              placeholder="Additional guidance for inspectors..."
                              rows={2}
                            />
                          </div>

                          <div className="flex items-center gap-4 pt-2">
                            <div className="flex items-center gap-2">
                              <Switch
                                checked={question.required}
                                onCheckedChange={(checked) => handleQuestionChange(index, 'required', checked)}
                              />
                              <Label className="text-sm">Required</Label>
                            </div>

                            {template.scoring_enabled && (
                              <div className="flex items-center gap-2">
                                <Switch
                                  checked={question.scoring_enabled}
                                  onCheckedChange={(checked) => handleQuestionChange(index, 'scoring_enabled', checked)}
                                />
                                <Label className="text-sm">Enable Scoring</Label>
                              </div>
                            )}
                          </div>
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleRemoveQuestion(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 3: Scheduling */}
        <TabsContent value="scheduling">
          <Card>
            <CardHeader>
              <CardTitle>Scheduling & Assignment</CardTitle>
              <CardDescription>Configure recurring schedules and unit assignments</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Recurrence Rule</Label>
                <Select
                  value={template.recurrence_rule || 'none'}
                  onValueChange={(value) => setTemplate({ ...template, recurrence_rule: value === 'none' ? null : value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="No recurring schedule" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No recurring schedule</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="quarterly">Quarterly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {template.recurrence_rule && (
                <div className="space-y-2">
                  <Label>Auto-Assignment Logic</Label>
                  <Select
                    value={template.auto_assign_logic || 'round_robin'}
                    onValueChange={(value) => setTemplate({ ...template, auto_assign_logic: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="round_robin">Round Robin</SelectItem>
                      <SelectItem value="least_loaded">Least Loaded</SelectItem>
                      <SelectItem value="specific_users">Specific Users</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    How inspections should be automatically assigned
                  </p>
                </div>
              )}

              <Separator />

              <div className="space-y-2">
                <Label>Assign to Units</Label>
                <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto border rounded-lg p-3">
                  {units.length === 0 ? (
                    <p className="col-span-2 text-sm text-muted-foreground text-center py-4">
                      No units available
                    </p>
                  ) : (
                    units.map((unit) => (
                      <div key={unit.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={`unit-${unit.id}`}
                          checked={template.unit_ids?.includes(unit.id) || false}
                          onChange={(e) => {
                            const newUnitIds = e.target.checked
                              ? [...(template.unit_ids || []), unit.id]
                              : (template.unit_ids || []).filter(id => id !== unit.id);
                            setTemplate({ ...template, unit_ids: newUnitIds });
                          }}
                          className="rounded"
                        />
                        <label htmlFor={`unit-${unit.id}`} className="text-sm cursor-pointer">
                          {unit.name}
                        </label>
                      </div>
                    ))
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  Select units that should use this inspection template
                </p>
              </div>

              <div className="space-y-2">
                <Label>Required Competency</Label>
                <Input
                  value={template.requires_competency || ''}
                  onChange={(e) => setTemplate({ ...template, requires_competency: e.target.value || null })}
                  placeholder="e.g., SAFETY-101, CONFINED-SPACE"
                />
                <p className="text-sm text-muted-foreground">
                  Competency code required to perform this inspection
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 4: Workflow */}
        <TabsContent value="workflow">
          <Card>
            <CardHeader>
              <CardTitle>Work Order & Workflow</CardTitle>
              <CardDescription>Configure automatic work order creation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg bg-amber-50 dark:bg-amber-950/20">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-600" />
                    <Label className="text-base">Auto-Create Work Order on Fail</Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Automatically create corrective work order when inspection fails
                  </p>
                </div>
                <Switch
                  checked={template.auto_create_work_order_on_fail}
                  onCheckedChange={(checked) => setTemplate({ ...template, auto_create_work_order_on_fail: checked })}
                />
              </div>

              {template.auto_create_work_order_on_fail && (
                <div className="space-y-2">
                  <Label>Work Order Priority</Label>
                  <Select
                    value={template.work_order_priority || 'normal'}
                    onValueChange={(value) => setTemplate({ ...template, work_order_priority: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    Priority level for automatically created work orders
                  </p>
                </div>
              )}

              <Separator />

              <div className="space-y-4 p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
                <div className="flex items-center gap-2">
                  <LinkIcon className="h-4 w-4 text-primary" />
                  <Label className="text-base">Integration Points</Label>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span>Links to Asset Management (if asset_id provided)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span>Creates Work Orders automatically on failure</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span>Tracks follow-up inspections</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-yellow-500" />
                    <span>Workflow approvals (configure in Workflows module)</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 5: Advanced */}
        <TabsContent value="advanced">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>Additional configuration options</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Template Version</Label>
                  <Input value={template.version || 1} disabled />
                  <p className="text-sm text-muted-foreground">
                    Version number (auto-incremented on changes)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Status</Label>
                  <Badge variant={template.is_active !== false ? 'default' : 'secondary'}>
                    {template.is_active !== false ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Analytics & Reporting
                </h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                    <div className="text-muted-foreground">Questions</div>
                    <div className="text-2xl font-bold">{template.questions.length}</div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                    <div className="text-muted-foreground">Units Assigned</div>
                    <div className="text-2xl font-bold">{template.unit_ids?.length || 0}</div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                    <div className="text-muted-foreground">Est. Duration</div>
                    <div className="text-2xl font-bold">
                      {template.estimated_duration_minutes ? `${template.estimated_duration_minutes}m` : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
                <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  Template Capabilities
                </h4>
                <ul className="text-sm space-y-1">
                  <li className="flex items-center gap-2">
                    <span className={template.scoring_enabled ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.scoring_enabled ? '✓' : '○'} Pass/Fail Scoring
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.require_gps ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.require_gps ? '✓' : '○'} GPS Location Capture
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.recurrence_rule ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.recurrence_rule ? '✓' : '○'} Recurring Schedule
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.auto_create_work_order_on_fail ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.auto_create_work_order_on_fail ? '✓' : '○'} Auto Work Order Creation
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.questions.some(q => q.photo_required) ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.questions.some(q => q.photo_required) ? '✓' : '○'} Photo Requirements
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.questions.some(q => q.signature_required) ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.questions.some(q => q.signature_required) ? '✓' : '○'} Signature Capture
                    </span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      </div>
    </ModernPageWrapper>
  );
};

export default EnhancedTemplateBuilderPage;
