// @ts-nocheck
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Plus, Edit, Trash2, Play, GitBranch, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkflowDesigner: React.FC = () => {
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    resource_type: 'inspection',
    steps: [{
      step_number: 1,
      name: '',
      approver_role: 'supervisor',
      approver_context: 'organization',
      approval_type: 'any',
      timeout_hours: 24,
      escalate_to_role: ''
    }],
    auto_start: false,
    notify_on_start: true,
    notify_on_complete: true
  });

  useEffect(() => {
    loadTemplates();
    loadRoles();
  }, []);

  const loadTemplates = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/workflows/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(response.data);
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/roles`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRoles(response.data);
    } catch (err) {
      console.error('Failed to load roles:', err);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/workflows/templates`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowCreateDialog(false);
      resetForm();
      loadTemplates();
    } catch (err) {
      console.error('Failed to create template:', err);
      alert('Failed to create workflow template');
    }
  };

  const handleUpdateTemplate = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(`${API}/workflows/templates/${editingTemplate.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowCreateDialog(false);
      setEditingTemplate(null);
      resetForm();
      loadTemplates();
    } catch (err) {
      console.error('Failed to update template:', err);
      alert('Failed to update workflow template');
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to deactivate this workflow template?')) return;
    
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${API}/workflows/templates/${templateId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadTemplates();
    } catch (err) {
      console.error('Failed to delete template:', err);
      alert(err.response?.data?.detail || 'Failed to delete workflow template');
    }
  };

  const resetForm: React.FC = () => {
    setFormData({
      name: '',
      description: '',
      resource_type: 'inspection',
      steps: [{
        step_number: 1,
        name: '',
        approver_role: 'supervisor',
        approver_context: 'organization',
        approval_type: 'any',
        timeout_hours: 24,
        escalate_to_role: ''
      }],
      auto_start: false,
      notify_on_start: true,
      notify_on_complete: true
    });
  };

  const addStep: React.FC = () => {
    setFormData({
      ...formData,
      steps: [...formData.steps, {
        step_number: formData.steps.length + 1,
        name: '',
        approver_role: 'supervisor',
        approver_context: 'organization',
        approval_type: 'any',
        timeout_hours: 24,
        escalate_to_role: ''
      }]
    });
  };

  const removeStep = (index) => {
    const newSteps = formData.steps.filter((_, i) => i !== index);
    newSteps.forEach((step, i) => step.step_number = i + 1);
    setFormData({ ...formData, steps: newSteps });
  };

  const updateStep = (index, field, value) => {
    const newSteps = [...formData.steps];
    newSteps[index][field] = value;
    setFormData({ ...formData, steps: newSteps });
  };

  const openEditDialog = (template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      resource_type: template.resource_type,
      steps: template.steps,
      auto_start: template.auto_start,
      notify_on_start: template.notify_on_start,
      notify_on_complete: template.notify_on_complete
    });
    setShowCreateDialog(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Workflow Designer</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Design multi-level approval workflows for your organization
          </p>
        </div>
        <Button onClick={() => { resetForm(); setShowCreateDialog(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          New Workflow
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-slate-600 dark:text-slate-400">Loading workflows...</p>
        </div>
      ) : templates.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <GitBranch className="h-12 w-12 mx-auto mb-4 text-slate-400" />
            <p className="text-slate-600 dark:text-slate-400 mb-4">
              No workflow templates yet. Create your first workflow!
            </p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Workflow
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map(template => (
            <Card key={template.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2">
                      {template.name}
                      {template.active ? (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                          Inactive
                        </span>
                      )}
                    </CardTitle>
                    <CardDescription>{template.description}</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEditDialog(template)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteTemplate(template.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm">
                    <Play className="h-4 w-4 mr-2 text-slate-500" />
                    <span className="font-medium">Resource:</span>
                    <span className="ml-2 text-slate-600">{template.resource_type}</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <GitBranch className="h-4 w-4 mr-2 text-slate-500" />
                    <span className="font-medium">Steps:</span>
                    <span className="ml-2 text-slate-600">{template.steps.length}</span>
                  </div>
                  <div className="border-t pt-3 mt-3">
                    <p className="text-xs font-semibold text-slate-700 mb-2">Approval Flow:</p>
                    <div className="space-y-2">
                      {template.steps.map((step, idx) => (
                        <div key={idx} className="flex items-center text-xs">
                          <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold mr-2">
                            {step.step_number}
                          </div>
                          <div className="flex-1">
                            <div className="font-medium">{step.name}</div>
                            <div className="text-slate-500">
                              {step.approver_role} • {step.timeout_hours}h timeout
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={(open) => {
        setShowCreateDialog(open);
        if (!open) {
          setEditingTemplate(null);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingTemplate ? 'Edit Workflow Template' : 'Create Workflow Template'}
            </DialogTitle>
            <DialogDescription>
              Define the approval steps and rules for this workflow
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Workflow Name</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Inspection Approval"
                />
              </div>
              <div>
                <Label>Resource Type</Label>
                <Select
                  value={formData.resource_type}
                  onValueChange={(value) => setFormData({ ...formData, resource_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="inspection">Inspection</SelectItem>
                    <SelectItem value="task">Task</SelectItem>
                    <SelectItem value="checklist">Checklist</SelectItem>
                    <SelectItem value="report">Report</SelectItem>
                    <SelectItem value="user_role_change">User Role Change</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Description</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe when this workflow should be used"
                rows={2}
              />
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-4">
                <Label className="text-base font-semibold">Approval Steps</Label>
                <Button type="button" size="sm" onClick={addStep}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add Step
                </Button>
              </div>

              <div className="space-y-4">
                {formData.steps.map((step, index) => (
                  <Card key={index}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">Step {step.step_number}</CardTitle>
                        {formData.steps.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeStep(index)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <Label>Step Name</Label>
                        <Input
                          value={step.name}
                          onChange={(e) => updateStep(index, 'name', e.target.value)}
                          placeholder="e.g., Supervisor Review"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Approver Role</Label>
                          <Select
                            value={step.approver_role}
                            onValueChange={(value) => updateStep(index, 'approver_role', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {roles && roles.length > 0 ? (
                                roles.map(role => (
                                  <SelectItem key={role.code} value={role.code}>
                                    {role.name}
                                  </SelectItem>
                                ))
                              ) : (
                                <SelectItem value="loading" disabled>Loading roles...</SelectItem>
                              )}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Context</Label>
                          <Select
                            value={step.approver_context}
                            onValueChange={(value) => updateStep(index, 'approver_context', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="own">Own Items</SelectItem>
                              <SelectItem value="team">Team</SelectItem>
                              <SelectItem value="branch">Branch</SelectItem>
                              <SelectItem value="region">Region</SelectItem>
                              <SelectItem value="organization">Organization</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label>Approval Type</Label>
                          <Select
                            value={step.approval_type}
                            onValueChange={(value) => updateStep(index, 'approval_type', value)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="any">Any One Approver</SelectItem>
                              <SelectItem value="all">All Must Approve</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Timeout (hours)</Label>
                          <Input
                            type="number"
                            value={step.timeout_hours}
                            onChange={(e) => updateStep(index, 'timeout_hours', parseInt(e.target.value))}
                          />
                        </div>
                      </div>
                      <div>
                        <Label>Escalate To (if timeout)</Label>
                        <Select
                          value={step.escalate_to_role || 'none'}
                          onValueChange={(value) => updateStep(index, 'escalate_to_role', value === 'none' ? '' : value)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="No escalation" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">No escalation</SelectItem>
                            {roles && roles.length > 0 && roles.map(role => (
                              <SelectItem key={role.code} value={role.code}>
                                {role.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateDialog(false);
                setEditingTemplate(null);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button onClick={editingTemplate ? handleUpdateTemplate : handleCreateTemplate}>
              {editingTemplate ? 'Update Workflow' : 'Create Workflow'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkflowDesigner;