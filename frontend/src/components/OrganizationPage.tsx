// @ts-nocheck
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '@/hooks/usePermissions';
import { PermissionGuard } from '@/components/PermissionGuard';
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
import { Building2, Users, Plus, ChevronRight, ChevronDown, Pencil, Trash2, UserPlus, AlertCircle, Link2, Unlink, ExternalLink, Eye } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LEVEL_NAMES = {
  1: 'Profile',
  2: 'Organisation',
  3: 'Company',
  4: 'Branch',
  5: 'Brand'
};

// Unified color configuration - hex values for inline styles
const LEVEL_COLORS = {
  1: { hex: '#3b82f6', bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500', name: 'Profile' },
  2: { hex: '#22c55e', bg: 'bg-green-500', text: 'text-green-500', border: 'border-green-500', name: 'Organisation' },
  3: { hex: '#a855f7', bg: 'bg-purple-500', text: 'text-purple-500', border: 'border-purple-500', name: 'Company' },
  4: { hex: '#f97316', bg: 'bg-orange-500', text: 'text-orange-500', border: 'border-orange-500', name: 'Branch' },
  5: { hex: '#ec4899', bg: 'bg-pink-500', text: 'text-pink-500', border: 'border-pink-500', name: 'Brand' }
};

const getLevelColors = (level: number) => {
  return LEVEL_COLORS[level] || { 
    hex: '#6b7280',
    bg: 'bg-gray-500', 
    text: 'text-gray-500', 
    border: 'border-gray-500', 
    name: 'Unknown' 
  };
};

const OrganizationNode: React.FC<any> = ({ node, onLinkExisting, onUnlink, onViewUsers, onViewDetails, expandedNodes, toggleNode, depth = 0 }) => {
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
          style={{ backgroundColor: colors.hex, color: 'white' }}
          className="px-4 py-2 rounded-md w-80 flex items-center justify-between text-sm font-semibold 
            hover:opacity-90 transition-opacity cursor-default shadow-sm"
          title={`${colors.name} level organizational unit`}
        >
          <span>{colors.name}</span>
          <span className="opacity-90">Level {node.level}</span>
          <Badge variant="secondary" className="bg-white/20 text-white border-white/30 text-xs">
            {userCount} users
          </Badge>
        </div>
        
        {/* Action Buttons - Streamlined for Management Only */}
        <div className="flex gap-1 ml-auto">
          {/* Link Existing - Only if not at max level */}
          {node.level < 5 && (
            <PermissionGuard 
              anyPermissions={['organization.update.organization']}
              tooltipMessage="No permission to link organizational units"
            >
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onLinkExisting(node)}
                data-testid={`link-existing-${node.id}`}
                title={`Link existing ${getLevelColors(node.level + 1)?.name || 'unit'}`}
              >
                <Link2 className="h-4 w-4" />
              </Button>
            </PermissionGuard>
          )}
          
          {/* Unlink - Only if entity has a parent */}
          {node.parent_id && (
            <PermissionGuard 
              anyPermissions={['organization.update.organization']}
              tooltipMessage="No permission to unlink organizational units"
            >
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onUnlink(node)}
                data-testid={`unlink-${node.id}`}
                title="Unlink from parent (makes orphaned)"
              >
                <Unlink className="h-4 w-4" />
              </Button>
            </PermissionGuard>
          )}
          
          {/* View Users */}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onViewUsers(node)}
            data-testid={`view-users-${node.id}`}
            title="View assigned users"
          >
            <Users className="h-4 w-4" />
          </Button>
          
          {/* View Details - Opens Settings for editing */}
          <PermissionGuard 
            anyPermissions={['organization.read.organization']}
            tooltipMessage="No permission to view details"
          >
            <Button
              size="sm"
              variant="ghost"
              onClick={() => onViewDetails(node)}
              data-testid={`view-details-${node.id}`}
              title="View/Edit details in Settings"
            >
              <Eye className="h-4 w-4" />
            </Button>
          </PermissionGuard>
        </div>
      </div>
      
      {isExpanded && hasChildren && (
        <div className="relative">
          {node.children.map((child: any) => (
            <OrganizationNode
              key={child.id}
              node={child}
              onLinkExisting={onLinkExisting}
              onUnlink={onUnlink}
              onViewUsers={onViewUsers}
              onViewDetails={onViewDetails}
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
  
  // Dialog states (streamlined - removed showCreateDialog and showEditDialog)
  const [showUsersDialog, setShowUsersDialog] = useState<boolean>(false);
  const [showInviteDialog, setShowInviteDialog] = useState<boolean>(false);
  const [showLinkDialog, setShowLinkDialog] = useState<boolean>(false);
  
  // Form states (removed formData for create/edit - now in Settings)
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [unitUsers, setUnitUsers] = useState<any[]>([]);
  const [inviteData, setInviteData] = useState<any>({
    user_id: '',
    unit_id: '',
    role: 'viewer',
  });
  const [availableUsers, setAvailableUsers] = useState<any[]>([]);
  const [linkData, setLinkData] = useState<any>({
    child_unit_id: '',
  });
  const [availableUnits, setAvailableUnits] = useState<any[]>([]);

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

  const handleUnlink = async (node: any) => {
    if (!window.confirm(`Unlink "${node.name}" from its parent? It will become an orphaned entity but won't be deleted.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API}/organizations/units/${node.id}/unlink`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`${node.name} has been unlinked successfully`);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to unlink unit');
    }
  };

  const handleViewDetails = (node: any) => {
    // Redirect to Settings page to edit entity
    alert(`To edit "${node.name}", go to Settings → Admin & Compliance → Organizational Entities`);
    // Optionally: navigate to settings
    // window.location.href = '/settings';
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

  const handleInviteUser = async () => {
    // Load available users based on RBAC
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API}/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAvailableUsers(response.data.users || response.data || []);
    } catch (err) {
      console.error('Failed to load users:', err);
      setAvailableUsers([]);
    }
    
    setInviteData({ user_id: '', unit_id: selectedNode?.id || '', role: 'viewer' });
    setShowInviteDialog(true);
  };

  const handleSubmitInvite = async (e: any) => {
    e.preventDefault();
    try {
      // Allocate existing user to organizational unit
      await axios.post(`${API}/organizations/units/${inviteData.unit_id}/assign-user`, {
        user_id: inviteData.user_id,
        unit_id: inviteData.unit_id,  // Required by Pydantic model
        role: inviteData.role
      });
      alert('User allocated successfully!');
      setShowInviteDialog(false);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to allocate user');
    }
  };

  const handleLinkExisting = async (parentNode: any) => {
    // Load available units at the next level that are unassigned (no parent)
    try {
      const token = localStorage.getItem('access_token');
      const nextLevel = parentNode.level + 1;
      const response = await axios.get(`${API}/organizations/units?level=${nextLevel}&unassigned=true`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAvailableUnits(response.data || []);
    } catch (err) {
      console.error('Failed to load available units:', err);
      setAvailableUnits([]);
    }
    
    setLinkData({ child_unit_id: '' });
    setSelectedNode(parentNode);
    setShowLinkDialog(true);
  };

  const handleSubmitLink = async (e: any) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/organizations/units/${selectedNode.id}/link-child`, linkData);
      alert('Unit linked successfully!');
      setShowLinkDialog(false);
      loadHierarchy();
    } catch (err: unknown) {
      alert((err as any).response?.data?.detail || 'Failed to link unit');
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
      title="Organization Structure" 
      subtitle="Manage hierarchy, link entities, and allocate users"
      actions={
        <Alert className="max-w-xl">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">
            <strong>Note:</strong> To create new entities with full details and logos, 
            go to <strong>Settings → Admin & Compliance → Organizational Entities</strong>
          </AlertDescription>
        </Alert>
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
                5-level organizational structure - Link entities and allocate users
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {[1, 2, 3, 4, 5].map((level, idx) => {
                  const colors = getLevelColors(level);
                  return (
                    <React.Fragment key={level}>
                      {idx > 0 && <ChevronRight className="h-5 w-5 text-muted-foreground" />}
                      <Badge 
                        style={{ backgroundColor: colors.hex, color: 'white' }}
                        className="px-3 py-1.5 text-sm font-semibold"
                      >
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
                    onLinkExisting={handleLinkExisting}
                    onUnlink={handleUnlink}
                    onViewUsers={handleViewUsers}
                    onViewDetails={handleViewDetails}
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
                Allocate User
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Allocate User Dialog */}
        <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Allocate User to {selectedNode?.name}</DialogTitle>
              <DialogDescription>
                Assign an existing user to this organizational unit
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmitInvite}>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="user-select">Select User</Label>
                  <Select
                    value={inviteData.user_id}
                    onValueChange={(value) => setInviteData({ ...inviteData, user_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a user..." />
                    </SelectTrigger>
                    <SelectContent>
                      {availableUsers.map((user) => (
                        <SelectItem key={user.id} value={user.id}>
                          {user.name} ({user.email}) - {user.role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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
                <Button type="submit">Allocate User</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Link Existing Unit Dialog */}
        <Dialog open={showLinkDialog} onOpenChange={setShowLinkDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Link Existing {getLevelColors(selectedNode?.level + 1)?.name} to {selectedNode?.name}</DialogTitle>
              <DialogDescription>
                Select an existing unit to link as a child. Only unassigned units at the next level are shown.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmitLink}>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="unit-select">Select {getLevelColors(selectedNode?.level + 1)?.name}</Label>
                  {availableUnits.length > 0 ? (
                    <Select
                      value={linkData.child_unit_id}
                      onValueChange={(value) => setLinkData({ child_unit_id: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={`Choose ${getLevelColors(selectedNode?.level + 1)?.name}...`} />
                      </SelectTrigger>
                      <SelectContent>
                        {availableUnits.map((unit) => (
                          <SelectItem key={unit.id} value={unit.id}>
                            {unit.name} (Level {unit.level})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        No unassigned {getLevelColors(selectedNode?.level + 1)?.name} units available. 
                        Create a new {getLevelColors(selectedNode?.level + 1)?.name} first or unlink an existing one.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </div>
              <DialogFooter className="mt-4">
                <Button type="button" variant="outline" onClick={() => setShowLinkDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={!linkData.child_unit_id || availableUnits.length === 0}>
                  Link Unit
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

      </div>
    </ModernPageWrapper>
  );
};

export default OrganizationPage;