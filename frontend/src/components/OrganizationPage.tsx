// @ts-nocheck
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { ModernPageWrapper } from '@/design-system/components';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Building2, Users, Plus, ChevronRight, ChevronDown, Pencil, Trash2, UserPlus, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LEVEL_NAMES = {
  1: 'Profile',
  2: 'Organisation',
  3: 'Company',
  4: 'Branch',
  5: 'Brand'
};

// Unified color configuration matching Role Management pattern
const LEVEL_COLORS = {
  1: { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500', name: 'Profile' },
  2: { bg: 'bg-green-500', text: 'text-green-500', border: 'border-green-500', name: 'Organisation' },
  3: { bg: 'bg-purple-500', text: 'text-purple-500', border: 'border-purple-500', name: 'Company' },
  4: { bg: 'bg-orange-500', text: 'text-orange-500', border: 'border-orange-500', name: 'Branch' },
  5: { bg: 'bg-pink-500', text: 'text-pink-500', border: 'border-pink-500', name: 'Brand' }
};

const getLevelColors = (level: number) => {
  return LEVEL_COLORS[level] || { 
    bg: 'bg-gray-500', 
    text: 'text-gray-500', 
    border: 'border-gray-500', 
    name: 'Unknown' 
  };
};

const OrganizationNode: React.FC<any> = ({ node, onAddChild, onEdit, onDelete, onViewUsers, expandedNodes, toggleNode, depth = 0 }) => {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expandedNodes[node.id];
  const userCount = node.user_count || 0;
  const colors = getLevelColors(node.level);

  return (
    <div className="relative">
      {/* Visual connection line */}
      {depth > 0 && (
        <div className="absolute left-2 top-0 bottom-0 w-px bg-slate-300 dark:bg-slate-600" />
      )}
      
      <div 
        className="flex items-center gap-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg px-2 transition-colors"
        style={{ marginLeft: `${depth * 24}px` }}
      >
        {hasChildren ? (
          <button
            onClick={() => toggleNode(node.id)}
            className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded z-10"
            data-testid={`toggle-node-${node.id}`}
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>
        ) : (
          <div className="w-6" />
        )}
        
        <Building2 className="h-4 w-4 text-slate-600" />
        
        <span className="font-medium w-48" data-testid={`node-name-${node.id}`}>{node.name}</span>
        
        {/* Equal Width Color Bar with Labels and Hover Effect */}
        <div 
          className={`${colors.bg} text-white px-4 py-2 rounded-md w-80 flex items-center justify-between text-sm font-semibold 
            hover:opacity-90 transition-opacity cursor-default shadow-sm`}
          title={`${colors.name} level organizational unit`}
        >
          <span>{colors.name}</span>
          <span className="opacity-90">Level {node.level}</span>
          <Badge variant="secondary" className="bg-white/20 text-white border-white/30 text-xs">
            {userCount} users
          </Badge>
        </div>
        
        {/* Action Buttons with Simple Title Tooltips */}
        <div className="flex gap-1 ml-auto">
          {node.level < 5 && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onAddChild(node)}
              data-testid={`add-child-${node.id}`}
              title={`Add child ${LEVEL_CONFIG[node.level + 1]?.name || 'unit'}`}
            >
              <Plus className="h-4 w-4" />
            </Button>
          )}
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onViewUsers(node)}
            data-testid={`view-users-${node.id}`}
            title="View assigned users"
          >
            <Users className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(node)}
            data-testid={`edit-${node.id}`}
            title={`Edit ${node.name}`}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(node)}
            data-testid={`delete-${node.id}`}
            title={`Delete ${node.name}`}
          >
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      </div>
      
      {isExpanded && hasChildren && (
        <div className="relative">
          {node.children.map((child: any) => (
            <OrganizationNode
              key={child.id}
              node={child}
              onAddChild={onAddChild}
              onEdit={onEdit}
              onDelete={onDelete}
              onViewUsers={onViewUsers}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const OrganizationPage = () => {
  // const { user } = useAuth();
  const [hierarchy, setHierarchy] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  
  // Persistent expand/collapse state with localStorage
  const [expandedNodes, setExpandedNodes] = useState<any>(() => {
    try {
      const saved = localStorage.getItem('org_hierarchy_expanded');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  
  // Dialog states
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [showEditDialog, setShowEditDialog] = useState<boolean>(false);
  const [showUsersDialog, setShowUsersDialog] = useState<boolean>(false);
  const [showInviteDialog, setShowInviteDialog] = useState<boolean>(false);
  
  // Form states
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [unitUsers, setUnitUsers] = useState<any[]>([]);
  const [formData, setFormData] = useState<{[key: string]: any}>({
    name: '',
    description: '',
    level: 1,
    parent_id: null,
  });
  const [inviteData, setInviteData] = useState<any>({
    email: '',
    unit_id: '',
    role: 'viewer',
  });

  useEffect(() => {
    loadHierarchy();
  }, []);

  // Persist expanded nodes to localStorage
  useEffect(() => {
    localStorage.setItem('org_hierarchy_expanded', JSON.stringify(expandedNodes));
  }, [expandedNodes]);

  const loadHierarchy = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/organizations/hierarchy`);
      setHierarchy(response.data);
      
      // Only auto-expand if no saved state exists
      const saved = localStorage.getItem('org_hierarchy_expanded');
      if (!saved) {
        // First time: Don't auto-expand anything (only Profile level visible)
        setExpandedNodes({});
      }
      
      setError('');
    } catch (err: unknown) {
      setError((err as any).response?.data?.detail || 'Failed to load organization hierarchy');
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = (nodeId: any) => {
    setExpandedNodes(prev => ({
      ...prev,
      [nodeId]: !prev[nodeId]
    }));
  };

  const handleCreateRoot = () => {
    setFormData({ name: '', description: '', level: 1, parent_id: null });
    setSelectedNode(null);
    setShowCreateDialog(true);
  };

  const handleAddChild = (parentNode: any) => {
    setFormData({
      name: '',
      description: '',
      level: parentNode.level + 1,
      parent_id: parentNode.id,
    });
    setSelectedNode(parentNode);
    setShowCreateDialog(true);
  };

  const handleEdit = (node: any) => {
    setFormData({
      name: node.name,
      description: node.description || '',
      level: node.level,
      parent_id: node.parent_id,
    });
    setSelectedNode(node);
    setShowEditDialog(true);
  };

  const handleDelete = async (node: any) => {
    if (!window.confirm(`Are you sure you want to delete "${node.name}"?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/organizations/units/${node.id}`);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to delete unit');
    }
  };

  const handleViewUsers = async (node: any) => {
    try {
      const response = await axios.get(`${API}/organizations/units/${node.id}/users`);
      setUnitUsers(response.data);
      setSelectedNode(node);
      setShowUsersDialog(true);
    } catch (err: unknown) {
      alert('Failed to load users');
    }
  };

  const handleSubmitCreate = async (e: any) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/organizations/units`, formData);
      setShowCreateDialog(false);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to create unit');
    }
  };

  const handleSubmitEdit = async (e: any) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/organizations/units/${selectedNode.id}`, {
        name: formData.name,
        description: formData.description,
      });
      setShowEditDialog(false);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to update unit');
    }
  };

  const handleInviteUser = () => {
    setInviteData({ email: '', unit_id: selectedNode?.id || '', role: 'viewer' });
    setShowInviteDialog(true);
  };

  const handleSubmitInvite = async (e: any) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/organizations/invitations`, inviteData);
      alert('Invitation sent successfully!');
      setShowInviteDialog(false);
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to send invitation');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <ModernPageWrapper 
      title="Organization" 
      subtitle="Manage organizational structure"
      actions={
        <Button onClick={handleCreateRoot} data-testid="create-root-unit-btn">
          <Plus className="h-4 w-4 mr-2" />
          Create Profile
        </Button>
      }
    >
      <div className="space-y-6">

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Hierarchy Tree</CardTitle>
            <CardDescription>
              <div className="text-sm text-muted-foreground mb-3">
                5-level organizational structure
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {[1, 2, 3, 4, 5].map((level, idx) => {
                  const colors = getLevelColors(level);
                  return (
                    <React.Fragment key={level}>
                      {idx > 0 && <ChevronRight className="h-5 w-5 text-muted-foreground" />}
                      <Badge className={`${colors.bg} text-white px-3 py-1.5 text-sm font-semibold`}>
                        {colors.name}
                      </Badge>
                    </React.Fragment>
                  );
                })}
              </div>
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Quick Stats Summary */}
            {hierarchy.length > 0 && (
              <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg flex gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-blue-500" />
                  <span className="font-semibold">{hierarchy.length}</span>
                  <span className="text-muted-foreground">units</span>
                </div>
                <span className="text-muted-foreground">•</span>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-green-500" />
                  <span className="font-semibold">
                    {hierarchy.reduce((sum, node) => {
                      const countNode = (n: any): number => {
                        let count = n.user_count || 0;
                        if (n.children) {
                          n.children.forEach((child: any) => {
                            count += countNode(child);
                          });
                        }
                        return count;
                      };
                      return sum + countNode(node);
                    }, 0)}
                  </span>
                  <span className="text-muted-foreground">total users</span>
                </div>
                <span className="text-muted-foreground">•</span>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">
                    {Math.max(...hierarchy.map((n: any) => {
                      const getMaxDepth = (node: any, depth: number): number => {
                        if (!node.children || node.children.length === 0) return depth;
                        return Math.max(...node.children.map((c: any) => getMaxDepth(c, depth + 1)));
                      };
                      return getMaxDepth(n, 1);
                    }))}
                  </span>
                  <span className="text-muted-foreground">levels deep</span>
                </div>
              </div>
            )}
            
            {hierarchy.length === 0 ? (
              <div className="text-center py-12 text-slate-500" data-testid="empty-hierarchy">
                <Building2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No organizational units yet. Create a root unit to get started.</p>
              </div>
            ) : (
              <div data-testid="hierarchy-tree">
                {hierarchy.map((node) => (
                  <OrganizationNode
                    key={node.id}
                    node={node}
                    onAddChild={handleAddChild}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onViewUsers={handleViewUsers}
                    expandedNodes={expandedNodes}
                    toggleNode={toggleNode}
                    depth={0}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Create Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent data-testid="create-unit-dialog">
            <DialogHeader>
              <DialogTitle>
                {selectedNode ? `Add ${LEVEL_NAMES[formData.level]} under ${selectedNode.name}` : 'Create Profile'}
              </DialogTitle>
              <DialogDescription>
                Create a new {LEVEL_NAMES[formData.level]} level unit
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmitCreate}>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    data-testid="unit-name-input"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    data-testid="unit-description-input"
                  />
                </div>
              </div>
              <DialogFooter className="mt-4">
                <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit" data-testid="submit-create-unit-btn">Create Unit</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Edit Dialog */}
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Unit</DialogTitle>
              <DialogDescription>Update unit information</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmitEdit}>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="edit-name">Name</Label>
                  <Input
                    id="edit-name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="edit-description">Description</Label>
                  <Textarea
                    id="edit-description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter className="mt-4">
                <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Update Unit</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* View Users Dialog */}
        <Dialog open={showUsersDialog} onOpenChange={setShowUsersDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Users in {selectedNode?.name}</DialogTitle>
              <DialogDescription>
                Manage users assigned to this unit
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-2">
              {unitUsers.length === 0 ? (
                <p className="text-center py-4 text-slate-500">No users assigned yet</p>
              ) : (
                unitUsers.map((item) => (
                  <div key={item.assignment_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{item.user.name}</p>
                      <p className="text-sm text-slate-500">{item.user.email}</p>
                    </div>
                    <Badge>{item.role}</Badge>
                  </div>
                ))
              )}
            </div>
            <DialogFooter>
              <Button onClick={handleInviteUser}>
                <UserPlus className="h-4 w-4 mr-2" />
                Invite User
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Invite User Dialog */}
        <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite User</DialogTitle>
              <DialogDescription>
                Send an invitation to join {selectedNode?.name}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmitInvite}>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="invite-email">Email</Label>
                  <Input
                    id="invite-email"
                    type="email"
                    value={inviteData.email}
                    onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="invite-role">Role</Label>
                  <Select
                    value={inviteData.role}
                    onValueChange={(value) => setInviteData({ ...inviteData, role: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="manager">Manager</SelectItem>
                      <SelectItem value="inspector">Inspector</SelectItem>
                      <SelectItem value="viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter className="mt-4">
                <Button type="button" variant="outline" onClick={() => setShowInviteDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit">Send Invitation</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </ModernPageWrapper>
  );
};

export default OrganizationPage;