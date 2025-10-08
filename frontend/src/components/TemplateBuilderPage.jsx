import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Plus, Trash2, GripVertical, Save, ArrowLeft } from 'lucide-react';

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

const TemplateBuilderPage = () => {
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
    questions: [],
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isEdit) {
      loadTemplate();
    }
  }, [templateId]);

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
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/inspections')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            {isEdit ? 'Edit Template' : 'Create Template'}
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            {isEdit ? 'Update inspection template' : 'Build a new inspection template'}
          </p>
        </div>
        <Button onClick={handleSave} disabled={loading} data-testid="save-template-btn">
          <Save className="h-4 w-4 mr-2" />
          {loading ? 'Saving...' : 'Save Template'}
        </Button>
      </div>

      {/* Basic Info */}
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
              data-testid="template-name-input"
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
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
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
                  At least one photo must be taken
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

      {/* Questions */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Questions</CardTitle>
              <CardDescription>Add questions to your inspection template</CardDescription>
            </div>
            <Button onClick={handleAddQuestion} size="sm" data-testid="add-question-btn">
              <Plus className="h-4 w-4 mr-2" />
              Add Question
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {template.questions.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <p>No questions yet. Click "Add Question" to get started.</p>
            </div>
          ) : (
            template.questions.map((question, index) => (
              <Card key={index} className="border-2">
                <CardContent className="pt-6 space-y-4">
                  <div className="flex items-start gap-4">
                    <GripVertical className="h-5 w-5 text-slate-400 mt-2" />
                    <div className="flex-1 space-y-4">
                      <div className="flex gap-2">
                        <Badge variant="outline">Q{index + 1}</Badge>
                        <Badge className="capitalize">{question.question_type.replace('_', ' ')}</Badge>
                        {question.required && <Badge variant="destructive">Required</Badge>}
                      </div>

                      <div className="space-y-2">
                        <Label>Question Text *</Label>
                        <Input
                          value={question.question_text}
                          onChange={(e) => handleQuestionChange(index, 'question_text', e.target.value)}
                          placeholder="Enter your question..."
                          data-testid={`question-text-${index}`}
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
                              {QUESTION_TYPES.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                  {type.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="flex items-end">
                          <div className="flex items-center space-x-2">
                            <Switch
                              checked={question.required}
                              onCheckedChange={(checked) => handleQuestionChange(index, 'required', checked)}
                            />
                            <Label>Required</Label>
                          </div>
                        </div>
                      </div>

                      {question.question_type === 'multiple_choice' && (
                        <div className="space-y-2">
                          <Label>Options (comma-separated)</Label>
                          <Input
                            value={question.options?.join(', ') || ''}
                            onChange={(e) =>
                              handleQuestionChange(
                                index,
                                'options',
                                e.target.value.split(',').map((s) => s.trim())
                              )
                            }
                            placeholder="Option 1, Option 2, Option 3"
                          />
                        </div>
                      )}

                      {template.scoring_enabled && (
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={question.scoring_enabled}
                            onCheckedChange={(checked) => handleQuestionChange(index, 'scoring_enabled', checked)}
                          />
                          <Label>Include in scoring</Label>
                        </div>
                      )}
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveQuestion(index)}
                      className="text-red-600"
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
    </div>
  );
};

export default TemplateBuilderPage;