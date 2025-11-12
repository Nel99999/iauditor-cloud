// @ts-nocheck
/**
 * Organizational Entities Management Component
 * Settings → Admin & Compliance → Organizational Entities
 * 
 * Purpose: Create and configure organizational entities with rich metadata
 * Features: 20 standard fields + unlimited custom fields
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Building2, Plus, Pencil, Trash2, Upload, Save, X,
  Building, Factory, Store, Briefcase, AlertCircle, Check, Link2, LinkOff
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import PhoneInput from 'react-phone-number-input';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ENTITY_TYPES = {
  profile: { level: 1, name: 'Profile', plural: 'Profiles', icon: Building2, color: '#3b82f6' },
  organisation: { level: 2, name: 'Organisation', plural: 'Organisations', icon: Building, color: '#22c55e' },
  company: { level: 3, name: 'Company', plural: 'Companies', icon: Factory, color: '#a855f7' },
  branch: { level: 4, name: 'Branch', plural: 'Branches', icon: Store, color: '#f97316' },
  brand: { level: 5, name: 'Brand', plural: 'Brands', icon: Briefcase, color: '#ec4899' },
};

const INDUSTRY_OPTIONS = [
  'Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail',
  'Construction', 'Education', 'Hospitality', 'Transportation', 'Other'
];

const OrganizationalEntitiesManager = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  // State for entities by type
  const [entities, setEntities] = useState({
    profile: [],
    organisation: [],
    company: [],
    branch: [],
    brand: [],
  });
  
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedEntityType, setSelectedEntityType] = useState('');
  const [selectedEntity, setSelectedEntity] = useState(null);
  
  // Form data
  const [formData, setFormData] = useState({
    entity_type: '',
    level: 1,
    name: '',
    description: '',
    logo_url: '',
    primary_color: '',
    secondary_color: '',
    address_street: '',
    address_city: '',
    address_state: '',
    address_country: '',
    address_postal_code: '',
    phone: '',
    email: '',
    website: '',
    tax_id: '',
    registration_number: '',
    established_date: '',
    industry: '',
    cost_center: '',
    budget_code: '',
    currency: 'USD',
    default_manager_id: '',
    custom_fields: {},
  });
  
  const [customFields, setCustomFields] = useState([]);
  const [availableManagers, setAvailableManagers] = useState([]);

  useEffect(() => {
    loadAllEntities();
    loadCustomFields();
    loadAvailableManagers();
  }, []);

  const loadAllEntities = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/entities`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Group entities by type
      const grouped = {
        profile: [],
        organisation: [],
        company: [],
        branch: [],
        brand: [],
      };
      
      (response.data || []).forEach(entity => {
        if (grouped[entity.entity_type]) {
          grouped[entity.entity_type].push(entity);
        }
      });
      
      setEntities(grouped);
    } catch (err) {
      console.error('Failed to load entities:', err);
      toast({
        title: 'Error',
        description: 'Failed to load organizational entities',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCustomFields = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/entities/custom-fields`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCustomFields(response.data || []);
    } catch (err) {
      console.error('Failed to load custom fields:', err);
    }
  };

  const loadAvailableManagers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAvailableManagers(response.data || []);
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const handleCreate = (entityType) => {
    const typeInfo = ENTITY_TYPES[entityType];
    setSelectedEntityType(entityType);
    setFormData({
      entity_type: entityType,
      level: typeInfo.level,
      name: '',
      description: '',
      logo_url: '',
      primary_color: typeInfo.color,
      secondary_color: '',
      address_street: '',
      address_city: '',
      address_state: '',
      address_country: '',
      address_postal_code: '',
      phone: '',
      email: '',
      website: '',
      tax_id: '',
      registration_number: '',
      established_date: '',
      industry: '',
      cost_center: '',
      budget_code: '',
      currency: 'USD',
      default_manager_id: '',
      custom_fields: {},
    });
    setShowCreateDialog(true);
  };

  const handleEdit = (entity) => {
    setSelectedEntity(entity);
    setSelectedEntityType(entity.entity_type);
    setFormData({
      entity_type: entity.entity_type,
      level: entity.level,
      name: entity.name || '',
      description: entity.description || '',
      logo_url: entity.logo_url || '',
      primary_color: entity.primary_color || '',
      secondary_color: entity.secondary_color || '',
      address_street: entity.address_street || '',
      address_city: entity.address_city || '',
      address_state: entity.address_state || '',
      address_country: entity.address_country || '',
      address_postal_code: entity.address_postal_code || '',
      phone: entity.phone || '',
      email: entity.email || '',
      website: entity.website || '',
      tax_id: entity.tax_id || '',
      registration_number: entity.registration_number || '',
      established_date: entity.established_date || '',
      industry: entity.industry || '',
      cost_center: entity.cost_center || '',
      budget_code: entity.budget_code || '',
      currency: entity.currency || 'USD',
      default_manager_id: entity.default_manager_id || '',
      custom_fields: entity.custom_fields || {},
    });
    setShowEditDialog(true);
  };

  const handleSubmitCreate = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/entities`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast({
        title: 'Success',
        description: `${ENTITY_TYPES[formData.entity_type].name} created successfully!`,
      });
      
      setShowCreateDialog(false);
      loadAllEntities();
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to create entity',
        variant: 'destructive',
      });
    }
  };

  const handleSubmitEdit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      await axios.put(`${API}/entities/${selectedEntity.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast({
        title: 'Success',
        description: `${ENTITY_TYPES[formData.entity_type].name} updated successfully!`,
      });
      
      setShowEditDialog(false);
      loadAllEntities();
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to update entity',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (entity) => {
    if (!confirm(`Are you sure you want to delete ${entity.name}?`)) return;
    
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(`${API}/entities/${entity.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast({
        title: 'Success',
        description: `${ENTITY_TYPES[entity.entity_type].name} deleted successfully!`,
      });
      
      loadAllEntities();
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to delete entity',
        variant: 'destructive',
      });
    }
  };

  const handleLogoUpload = async (e, entityId = null) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formDataUpload = new FormData();
    formDataUpload.append('file', file);
    
    try {
      const token = localStorage.getItem('access_token');
      const uploadEntityId = entityId || (selectedEntity?.id || 'temp');
      
      const response = await axios.post(
        `${API}/entities/${uploadEntityId}/upload-logo`,
        formDataUpload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setFormData(prev => ({
        ...prev,
        logo_url: response.data.logo_url
      }));
      
      toast({
        title: 'Success',
        description: 'Logo uploaded successfully!',
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to upload logo',
        variant: 'destructive',
      });
    }
  };

  const renderEntityList = (entityType) => {
    const typeInfo = ENTITY_TYPES[entityType];
    const Icon = typeInfo.icon;
    const entityList = entities[entityType] || [];

    return (
      <Card key={entityType} className="mb-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon className="h-5 w-5" style={{ color: typeInfo.color }} />
              <CardTitle>{typeInfo.plural} (Level {typeInfo.level})</CardTitle>
            </div>
            <Button onClick={() => handleCreate(entityType)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create New {typeInfo.name}
            </Button>
          </div>
          <CardDescription>
            Manage {typeInfo.plural.toLowerCase()} with full details, logos, and business information
          </CardDescription>
        </CardHeader>
        <CardContent>
          {entityList.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Icon className="h-12 w-12 mx-auto mb-2 opacity-20" />
              <p>No {typeInfo.plural.toLowerCase()} configured yet.</p>
              <p className="text-sm">Click "Create New {typeInfo.name}" to get started.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {entityList.map(entity => (
                <div
                  key={entity.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  {/* Logo */}
                  <div className="flex-shrink-0">
                    {entity.logo_url ? (
                      <img
                        src={entity.logo_url.startsWith('http') ? entity.logo_url : `${BACKEND_URL}${entity.logo_url}`}
                        alt={entity.name}
                        className="h-12 w-12 object-cover rounded"
                      />
                    ) : (
                      <div
                        className="h-12 w-12 rounded flex items-center justify-center text-white font-bold"
                        style={{ backgroundColor: entity.primary_color || typeInfo.color }}
                      >
                        {entity.name.substring(0, 2).toUpperCase()}
                      </div>
                    )}
                  </div>
                  
                  {/* Info */}
                  <div className="flex-1">
                    <h4 className="font-semibold">{entity.name}</h4>
                    <div className="flex gap-2 text-sm text-muted-foreground">
                      {entity.industry && <span>{entity.industry}</span>}
                      {entity.address_city && <span>• {entity.address_city}</span>}
                      {entity.tax_id && <span>• Tax ID: {entity.tax_id}</span>}
                    </div>
                  </div>
                  
                  {/* Status */}
                  <div>
                    {entity.parent_id ? (
                      <Badge variant="default" className="gap-1">
                        <Link2 className="h-3 w-3" />
                        Linked
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="gap-1">
                        <LinkOff className="h-3 w-3" />
                        Not Linked
                      </Badge>
                    )}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" onClick={() => handleEdit(entity)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(entity)}
                      disabled={entity.parent_id}
                      title={entity.parent_id ? "Unlink from hierarchy first" : "Delete entity"}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderEntityForm = () => {
    const typeInfo = ENTITY_TYPES[selectedEntityType] || ENTITY_TYPES.profile;
    
    return (
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="basic">Basic</TabsTrigger>
          <TabsTrigger value="contact">Contact</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="business">Business</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
        </TabsList>
        
        {/* Tab 1: Basic Information */}
        <TabsContent value="basic" className="space-y-4">
          <div>
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder={`Enter ${typeInfo.name.toLowerCase()} name`}
              required
            />
          </div>
          
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Enter description"
              rows={3}
            />
          </div>
          
          <div>
            <Label htmlFor="industry">Industry</Label>
            <Select
              value={formData.industry}
              onValueChange={(value) => setFormData({...formData, industry: value})}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select industry" />
              </SelectTrigger>
              <SelectContent>
                {INDUSTRY_OPTIONS.map(ind => (
                  <SelectItem key={ind} value={ind}>{ind}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </TabsContent>
        
        {/* Tab 2: Contact & Location */}
        <TabsContent value="contact" className="space-y-4">
          <div>
            <Label htmlFor="address_street">Street Address</Label>
            <Input
              id="address_street"
              value={formData.address_street}
              onChange={(e) => setFormData({...formData, address_street: e.target.value})}
              placeholder="123 Main Street"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="address_city">City</Label>
              <Input
                id="address_city"
                value={formData.address_city}
                onChange={(e) => setFormData({...formData, address_city: e.target.value})}
                placeholder="Johannesburg"
              />
            </div>
            <div>
              <Label htmlFor="address_country">Country</Label>
              <Input
                id="address_country"
                value={formData.address_country}
                onChange={(e) => setFormData({...formData, address_country: e.target.value})}
                placeholder="South Africa"
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="phone">Phone Number</Label>
            <PhoneInput
              international
              defaultCountry="ZA"
              value={formData.phone}
              onChange={(value) => setFormData({...formData, phone: value || ''})}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="contact@company.com"
            />
          </div>
          
          <div>
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              type="url"
              value={formData.website}
              onChange={(e) => setFormData({...formData, website: e.target.value})}
              placeholder="https://company.com"
            />
          </div>
        </TabsContent>
        
        {/* Tab 3: Branding */}
        <TabsContent value="branding" className="space-y-4">
          <div>
            <Label htmlFor="logo">Logo</Label>
            <div className="flex items-center gap-4">
              {formData.logo_url && (
                <img
                  src={formData.logo_url.startsWith('http') ? formData.logo_url : `${BACKEND_URL}${formData.logo_url}`}
                  alt="Logo preview"
                  className="h-20 w-20 object-cover rounded border"
                />
              )}
              <div>
                <Input
                  id="logo"
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleLogoUpload(e, selectedEntity?.id)}
                  className="mb-2"
                />
                <p className="text-xs text-muted-foreground">
                  PNG, JPG, or SVG (max 2MB)
                </p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="primary_color">Primary Brand Color</Label>
              <div className="flex gap-2">
                <Input
                  id="primary_color"
                  type="color"
                  value={formData.primary_color || '#3b82f6'}
                  onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                  className="w-20 h-10"
                />
                <Input
                  value={formData.primary_color || ''}
                  onChange={(e) => setFormData({...formData, primary_color: e.target.value})}
                  placeholder="#3b82f6"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="secondary_color">Secondary Color</Label>
              <div className="flex gap-2">
                <Input
                  id="secondary_color"
                  type="color"
                  value={formData.secondary_color || '#64748b'}
                  onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                  className="w-20 h-10"
                />
                <Input
                  value={formData.secondary_color || ''}
                  onChange={(e) => setFormData({...formData, secondary_color: e.target.value})}
                  placeholder="#64748b"
                />
              </div>
            </div>
          </div>
        </TabsContent>
        
        {/* Tab 4: Business Details */}
        <TabsContent value="business" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="tax_id">Tax ID / VAT Number</Label>
              <Input
                id="tax_id"
                value={formData.tax_id}
                onChange={(e) => setFormData({...formData, tax_id: e.target.value})}
                placeholder="1234567890"
              />
            </div>
            <div>
              <Label htmlFor="registration_number">Registration Number</Label>
              <Input
                id="registration_number"
                value={formData.registration_number}
                onChange={(e) => setFormData({...formData, registration_number: e.target.value})}
                placeholder="REG-123456"
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="established_date">Established Date</Label>
            <Input
              id="established_date"
              type="date"
              value={formData.established_date}
              onChange={(e) => setFormData({...formData, established_date: e.target.value})}
            />
          </div>
          
          <div>
            <Label htmlFor="default_manager">Default Manager</Label>
            <Select
              value={formData.default_manager_id}
              onValueChange={(value) => setFormData({...formData, default_manager_id: value})}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select manager" />
              </SelectTrigger>
              <SelectContent>
                {availableManagers.map(manager => (
                  <SelectItem key={manager.id} value={manager.id}>
                    {manager.name} ({manager.role})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </TabsContent>
        
        {/* Tab 5: Financial */}
        <TabsContent value="financial" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="cost_center">Cost Center Code</Label>
              <Input
                id="cost_center"
                value={formData.cost_center}
                onChange={(e) => setFormData({...formData, cost_center: e.target.value})}
                placeholder="CC-1234"
              />
            </div>
            <div>
              <Label htmlFor="budget_code">Budget Code</Label>
              <Input
                id="budget_code"
                value={formData.budget_code}
                onChange={(e) => setFormData({...formData, budget_code: e.target.value})}
                placeholder="BUD-1234"
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="currency">Currency</Label>
            <Select
              value={formData.currency}
              onValueChange={(value) => setFormData({...formData, currency: value})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="USD">USD - US Dollar</SelectItem>
                <SelectItem value="ZAR">ZAR - South African Rand</SelectItem>
                <SelectItem value="EUR">EUR - Euro</SelectItem>
                <SelectItem value="GBP">GBP - British Pound</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </TabsContent>
      </Tabs>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">Loading organizational entities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">Organizational Entities</h3>
          <p className="text-sm text-muted-foreground">
            Create and configure organizational entities with complete details, logos, and business information.
            Use the Organization Structure page to link them into hierarchy.
          </p>
        </div>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <strong>Master & Developer Only:</strong> Entity configuration affects the entire organization.
          After creating entities here, use the Organization Structure page to link them into the hierarchy tree.
        </AlertDescription>
      </Alert>

      {/* Render entity lists for all 5 levels */}
      {Object.keys(ENTITY_TYPES).map(renderEntityList)}

      {/* Create Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Create New {ENTITY_TYPES[selectedEntityType]?.name}
            </DialogTitle>
            <DialogDescription>
              Configure all details for this {ENTITY_TYPES[selectedEntityType]?.name.toLowerCase()}.
              You can link it to the hierarchy later.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmitCreate}>
            {renderEntityForm()}
            
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button type="submit">
                <Save className="h-4 w-4 mr-2" />
                Create {ENTITY_TYPES[selectedEntityType]?.name}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Edit {ENTITY_TYPES[selectedEntityType]?.name}: {selectedEntity?.name}
            </DialogTitle>
            <DialogDescription>
              Update details for this {ENTITY_TYPES[selectedEntityType]?.name.toLowerCase()}.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmitEdit}>
            {renderEntityForm()}
            
            <DialogFooter className="mt-6">
              <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)}>
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button type="submit">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OrganizationalEntitiesManager;
