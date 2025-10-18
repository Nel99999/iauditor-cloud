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
import { 
  Plus, Trash2, Save, ArrowLeft, Image, FileSignature,
  Settings, Calendar, AlertTriangle, BarChart3, Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EnhancedChecklistBuilderPage = () => {
  const navigate = useNavigate();
  const { templateId } = useParams();
  const isEdit = !!templateId;

  const [template, setTemplate] = useState({
    name: '',
    description: '',
    category: 'daily',
    frequency: 'daily',
    scheduled_time: null,
    // V1 Enhancement fields
    unit_ids: [],
    asset_type_ids: [],
    shift_based: false,
    time_limit_minutes: null,
    requires_supervisor_approval: false,
    scoring_enabled: false,
    pass_percentage: 80,
    auto_create_work_order_on_fail: false,
    work_order_priority: 'normal',
    items: [],
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
      const response = await axios.get(`${API}/checklists/templates/${templateId}`);
      setTemplate(response.data);
    } catch (err) {
      console.error('Failed to load template:', err);
      alert('Failed to load template');
      navigate('/checklists');
    }
  };

  const handleAddItem = () => {
    setTemplate({
      ...template,
      items: [
        ...template.items,
        {
          text: '',
          required: true,
          order: template.items.length,
          photo_required: false,
          min_photos: 0,
          max_photos: 10,
          signature_required: false,
          help_text: '',
          scoring_enabled: template.scoring_enabled,
          pass_score: null,
        },
      ],
    });
  };

  const handleRemoveItem = (index) => {
    setTemplate({
      ...template,
      items: template.items.filter((_, i) => i !== index),
    });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...template.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setTemplate({ ...template, items: newItems });
  };

  const handleSave = async () => {
    if (!template.name.trim()) {
      alert('Please enter a template name');
      return;
    }

    if (template.items.length === 0) {
      alert('Please add at least one item');
      return;
    }

    try {
      setLoading(true);
      if (isEdit) {
        await axios.put(`${API}/checklists/templates/${templateId}`, template);
      } else {
        await axios.post(`${API}/checklists/templates`, template);
      }
      navigate('/checklists');
    } catch (err) {
      console.error('Failed to save template:', err);
      alert('Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper 
      title={isEdit ? 'Edit Checklist' : 'Enhanced Checklist Builder'} 
      subtitle={isEdit ? 'Update checklist template' : 'Build advanced checklist templates'}
      actions={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/checklists')}>
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
          <TabsTrigger value="items">
            <FileSignature className="h-4 w-4 mr-2" />
            Items
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
                  placeholder="e.g., Daily Opening Checklist"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={template.description}
                  onChange={(e) => setTemplate({ ...template, description: e.target.value })}
                  placeholder="Describe what this checklist covers..."
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
                      <SelectItem value="opening">Opening</SelectItem>
                      <SelectItem value="closing">Closing</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="safety">Safety</SelectItem>
                      <SelectItem value="quality">Quality</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="time_limit">Time Limit (minutes)</Label>
                  <Input
                    id="time_limit"
                    type="number"
                    min="1"
                    value={template.time_limit_minutes || ''}
                    onChange={(e) => setTemplate({ ...template, time_limit_minutes: parseInt(e.target.value) || null })}
                    placeholder="e.g., 15"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Scoring Enabled</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable pass/fail scoring
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
                    <Label>Shift-Based</Label>
                    <p className="text-sm text-muted-foreground">
                      Auto-create for each shift
                    </p>
                  </div>
                  <Switch
                    checked={template.shift_based}
                    onCheckedChange={(checked) => setTemplate({ ...template, shift_based: checked })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Require Supervisor Approval</Label>
                    <p className="text-sm text-muted-foreground">
                      Supervisor must approve completion
                    </p>
                  </div>
                  <Switch
                    checked={template.requires_supervisor_approval}
                    onCheckedChange={(checked) => setTemplate({ ...template, requires_supervisor_approval: checked })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 2: Items */}
        <TabsContent value="items">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Checklist Items</CardTitle>
                  <CardDescription>
                    Configure items with photo, signature requirements
                  </CardDescription>
                </div>
                <Button onClick={handleAddItem} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Item
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {template.items.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileSignature className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No items added yet</p>
                  <p className="text-sm">Click "Add Item" to get started</p>
                </div>
              ) : (
                template.items.map((item, index) => (
                  <Card key={index} className="border-l-4 border-l-primary/30">
                    <CardContent className="pt-6 space-y-4">
                      <div className="flex items-start justify-between gap-4">
                        <Badge variant="outline" className="mt-1">{index + 1}</Badge>
                        <div className="flex-1 space-y-4">
                          <div className="space-y-2">
                            <Label>Item Text *</Label>
                            <Input
                              value={item.text}
                              onChange={(e) => handleItemChange(index, 'text', e.target.value)}
                              placeholder="Enter checklist item..."
                            />
                          </div>

                          {/* Photo Requirements */}
                          <div className="space-y-3 bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Image className="h-4 w-4 text-primary" />
                                <Label>Photo Required</Label>
                              </div>
                              <Switch
                                checked={item.photo_required}
                                onCheckedChange={(checked) => handleItemChange(index, 'photo_required', checked)}
                              />
                            </div>

                            {item.photo_required && (
                              <div className="grid grid-cols-2 gap-4 mt-2">
                                <div className="space-y-2">
                                  <Label className="text-sm">Min Photos</Label>
                                  <Input
                                    type="number"
                                    min="0"
                                    max={item.max_photos || 10}
                                    value={item.min_photos || 0}
                                    onChange={(e) => handleItemChange(index, 'min_photos', parseInt(e.target.value) || 0)}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label className="text-sm">Max Photos</Label>
                                  <Input
                                    type="number"
                                    min={item.min_photos || 0}
                                    max="20"
                                    value={item.max_photos || 10}
                                    onChange={(e) => handleItemChange(index, 'max_photos', parseInt(e.target.value) || 10)}
                                  />
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Signature Required */}
                          <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-900 p-4 rounded-lg">
                            <div className="flex items-center gap-2">
                              <FileSignature className="h-4 w-4 text-primary" />
                              <Label>Signature Required</Label>
                            </div>
                            <Switch
                              checked={item.signature_required}
                              onCheckedChange={(checked) => handleItemChange(index, 'signature_required', checked)}
                            />
                          </div>

                          {/* Help Text */}
                          <div className="space-y-2">
                            <Label>Help Text</Label>
                            <Textarea
                              value={item.help_text || ''}
                              onChange={(e) => handleItemChange(index, 'help_text', e.target.value)}
                              placeholder="Additional guidance..."
                              rows={2}
                            />
                          </div>

                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                              <Switch
                                checked={item.required}
                                onCheckedChange={(checked) => handleItemChange(index, 'required', checked)}
                              />
                              <Label className="text-sm">Required</Label>
                            </div>
                          </div>
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                          onClick={() => handleRemoveItem(index)}
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
              <CardDescription>Configure frequency and unit assignments</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Frequency</Label>
                  <Select
                    value={template.frequency}
                    onValueChange={(value) => setTemplate({ ...template, frequency: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="per_shift">Per Shift</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Scheduled Time</Label>
                  <Input
                    type="time"
                    value={template.scheduled_time || ''}
                    onChange={(e) => setTemplate({ ...template, scheduled_time: e.target.value || null })}
                  />
                </div>
              </div>

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
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 4: Workflow */}
        <TabsContent value="workflow">
          <Card>
            <CardHeader>
              <CardTitle>Work Order & Approval</CardTitle>
              <CardDescription>Configure automatic actions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg bg-amber-50 dark:bg-amber-950/20">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-600" />
                    <Label className="text-base">Auto-Create Work Order on Fail</Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Automatically create work order when checklist fails
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
                    value={template.work_order_priority}
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
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 5: Advanced */}
        <TabsContent value="advanced">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>Additional configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                  <div className="text-muted-foreground">Items</div>
                  <div className="text-2xl font-bold">{template.items.length}</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                  <div className="text-muted-foreground">Units</div>
                  <div className="text-2xl font-bold">{template.unit_ids?.length || 0}</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                  <div className="text-muted-foreground">Time Limit</div>
                  <div className="text-2xl font-bold">
                    {template.time_limit_minutes ? `${template.time_limit_minutes}m` : 'None'}
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
                      {template.scoring_enabled ? '✓' : '○'} Scoring Enabled
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.shift_based ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.shift_based ? '✓' : '○'} Shift-Based
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.auto_create_work_order_on_fail ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.auto_create_work_order_on_fail ? '✓' : '○'} Auto Work Order
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.items.some(i => i.photo_required) ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.items.some(i => i.photo_required) ? '✓' : '○'} Photo Requirements
                    </span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className={template.items.some(i => i.signature_required) ? 'text-green-600' : 'text-muted-foreground'}>
                      {template.items.some(i => i.signature_required) ? '✓' : '○'} Signature Required
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

export default EnhancedChecklistBuilderPage;
