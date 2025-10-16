import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2, Save, ArrowLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChecklistTemplateBuilder = () => {
  const navigate = useNavigate();
  const { templateId } = useParams();
  const isEdit = !!templateId;

  const [template, setTemplate] = useState<{
    name: string;
    description: string;
    category: string;
    frequency: string;
    scheduled_time: string;
    items: Array<{text: string; required: boolean; order: number}>;
  }>({
    name: '',
    description: '',
    category: 'daily',
    frequency: 'daily',
    scheduled_time: '',
    items: [],
  });
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isEdit) loadTemplate();
  }, [templateId]);

  const loadTemplate = async () => {
    try {
      const response = await axios.get(`${API}/checklists/templates/${templateId}`);
      setTemplate(response.data);
    } catch (err: unknown) {
      alert('Failed to load template');
      navigate('/checklists');
    }
  };

  const handleAddItem = () => {
    setTemplate({
      ...template,
      items: [...template.items, { text: '', required: true, order: template.items.length }],
    });
  };

  const handleRemoveItem = (index: any) => {
    setTemplate({
      ...template,
      items: template.items.filter((_: any, i: number) => i !== index),
    });
  };

  const handleItemChange = (index: number, value: any) => {
    const newItems = [...template.items];
    newItems[index] = { ...newItems[index], text: value };
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
    } catch (err: unknown) {
      alert('Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/checklists')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            {isEdit ? 'Edit Template' : 'Create Template'}
          </h1>
        </div>
        <Button onClick={handleSave} disabled={loading} data-testid="save-checklist-template-btn">
          <Save className="h-4 w-4 mr-2" />
          {loading ? 'Saving...' : 'Save Template'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Template Name *</Label>
            <Input
              value={template.name}
              onChange={(e) => setTemplate({ ...template, name: e.target.value })}
              placeholder="e.g., Opening Checklist"
              data-testid="checklist-name-input"
            />
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={template.description}
              onChange={(e) => setTemplate({ ...template, description: e.target.value })}
              placeholder="Describe this checklist..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Category</Label>
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
                </SelectContent>
              </Select>
            </div>

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
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Checklist Items</CardTitle>
            <Button onClick={handleAddItem} size="sm" data-testid="add-checklist-item-btn">
              <Plus className="h-4 w-4 mr-2" />
              Add Item
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {template.items.length === 0 ? (
            <p className="text-center py-8 text-slate-500">No items yet. Click "Add Item" to get started.</p>
          ) : (
            template.items.map((item: any, index: number) => (
              <div key={index} className="flex gap-2">
                <Input
                  value={item.text}
                  onChange={(e) => handleItemChange(index, e.target.value)}
                  placeholder={`Item ${index + 1}`}
                  data-testid={`checklist-item-${index}`}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveItem(index)}
                  className="text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ChecklistTemplateBuilder;
