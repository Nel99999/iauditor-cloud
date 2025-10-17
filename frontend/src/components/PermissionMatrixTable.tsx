// @ts-nocheck
import React, { useState, useEffect, Fragment } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronRight, Lock, Save, RotateCcw, Search } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Role abbreviation mapping with full names
const ROLE_ABBREV = {
  'developer': { abbrev: 'Dev', full: 'Developer', level: 1 },
  'master': { abbrev: 'Mst', full: 'Master', level: 2 },
  'admin': { abbrev: 'Adm', full: 'Admin', level: 3 },
  'operations_manager': { abbrev: 'OpMg', full: 'Operations Manager', level: 4 },
  'team_lead': { abbrev: 'TmLd', full: 'Team Lead', level: 5 },
  'manager': { abbrev: 'Mgr', full: 'Manager', level: 6 },
  'supervisor': { abbrev: 'Sup', full: 'Supervisor', level: 7 },
  'inspector': { abbrev: 'Ins', full: 'Inspector', level: 8 },
  'operator': { abbrev: 'Opr', full: 'Operator', level: 9 },
  'viewer': { abbrev: 'Viw', full: 'Viewer', level: 10 }
};

const PermissionMatrixTable = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [roles, setRoles] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [assignments, setAssignments] = useState<any>({});
  const [changes, setChanges] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterResource, setFilterResource] = useState('all');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadMatrix();
  }, []);

  const loadMatrix = async () => {
    try {
      setLoading(true);
      const [rolesRes, permsRes] = await Promise.all([
        axios.get(`${API}/roles`),
        axios.get(`${API}/permissions`)
      ]);

      setRoles(rolesRes.data.sort((a, b) => a.level - b.level));
      setPermissions(permsRes.data);

      // Load assignments for each role
      const assignMap: any = {};
      for (const role of rolesRes.data) {
        try {
          const perms = await axios.get(`${API}/roles/${role.id}/permissions`);
          assignMap[role.id] = perms.data.map((p: any) => p.permission_id);
        } catch (err) {
          assignMap[role.id] = [];
        }
      }
      setAssignments(assignMap);
      setChanges({});
    } catch (err) {
      console.error('Failed to load matrix:', err);
      toast({
        title: 'Error',
        description: 'Failed to load permission matrix',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const togglePermission = (roleId: string, permId: string, roleCode: string, isSystemRole: boolean) => {
    // Access control: Only Developer can edit system roles
    if (isSystemRole && user?.role !== 'developer') {
      toast({
        title: 'Access Denied',
        description: 'Only Developer role can edit system role permissions',
        variant: 'destructive'
      });
      return;
    }

    const currentlyHas = assignments[roleId]?.includes(permId) || false;
    const changeKey = `${roleId}_${permId}`;

    // Update assignments optimistically
    const newAssignments = { ...assignments };
    if (currentlyHas) {
      newAssignments[roleId] = newAssignments[roleId].filter(p => p !== permId);
    } else {
      newAssignments[roleId] = [...(newAssignments[roleId] || []), permId];
    }
    setAssignments(newAssignments);

    // Track change
    const newChanges = { ...changes };
    if (!newChanges[roleId]) {
      newChanges[roleId] = { added: [], removed: [] };
    }

    if (currentlyHas) {
      // Remove permission
      newChanges[roleId].removed.push(permId);
      newChanges[roleId].added = newChanges[roleId].added.filter(p => p !== permId);
    } else {
      // Add permission
      newChanges[roleId].added.push(permId);
      newChanges[roleId].removed = newChanges[roleId].removed.filter(p => p !== permId);
    }

    // Clean up empty changes
    if (newChanges[roleId].added.length === 0 && newChanges[roleId].removed.length === 0) {
      delete newChanges[roleId];
    }

    setChanges(newChanges);
  };

  const handleSaveAll = async () => {
    if (Object.keys(changes).length === 0) {
      toast({ title: 'No Changes', description: 'No pending changes to save' });
      return;
    }

    setSaving(true);
    let totalUpdated = 0;

    try {
      for (const [roleId, change] of Object.entries(changes)) {
        // Add permissions
        if (change.added.length > 0) {
          await axios.post(`${API}/roles/${roleId}/permissions/bulk`, change.added);
          totalUpdated += change.added.length;
        }

        // Remove permissions
        for (const permId of change.removed) {
          await axios.delete(`${API}/roles/${roleId}/permissions/${permId}`);
          totalUpdated += 1;
        }
      }

      toast({
        title: 'Success',
        description: `${totalUpdated} permission(s) updated across ${Object.keys(changes).length} role(s)`,
      });

      setChanges({});
      await loadMatrix();
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to save some changes',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (Object.keys(changes).length === 0) return;
    if (confirm('Discard all pending changes?')) {
      loadMatrix();
    }
  };

  const toggleSection = (resource: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(resource)) {
      newExpanded.delete(resource);
    } else {
      newExpanded.add(resource);
    }
    setExpandedSections(newExpanded);
  };

  // Group permissions by resource
  const groupedPermissions = permissions.reduce((acc, perm) => {
    const resource = perm.resource_type || 'other';
    if (!acc[resource]) acc[resource] = [];
    acc[resource].push(perm);
    return acc;
  }, {});

  // Sort permissions within each group
  Object.keys(groupedPermissions).forEach(resource => {
    groupedPermissions[resource].sort((a, b) => {
      const orderA = `${a.action}.${a.scope}`;
      const orderB = `${b.action}.${b.scope}`;
      return orderA.localeCompare(orderB);
    });
  });

  // Filter permissions
  const filteredResources = Object.keys(groupedPermissions)
    .filter(resource => filterResource === 'all' || resource === filterResource)
    .filter(resource => {
      if (!searchTerm) return true;
      const resourcePerms = groupedPermissions[resource];
      return resourcePerms.some(p => 
        p.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        `${p.resource_type}.${p.action}.${p.scope}`.includes(searchTerm.toLowerCase())
      );
    })
    .sort();

  const changeCount = Object.values(changes).reduce((sum: number, c: any) => 
    sum + c.added.length + c.removed.length, 0
  );

  const canEditSystemRoles = user?.role === 'developer';

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Permission Matrix</CardTitle>
              <CardDescription>
                Configure role permissions - {!canEditSystemRoles && '🔒 Only Developer can edit system roles'}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {changeCount > 0 && (
                <Button variant="outline" size="sm" onClick={handleReset}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
              )}
              <Button 
                onClick={handleSaveAll} 
                disabled={saving || changeCount === 0}
                size="sm"
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : `Save ${changeCount > 0 ? `${changeCount} Changes` : 'Changes'}`}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search permissions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
            <select
              value={filterResource}
              onChange={(e) => setFilterResource(e.target.value)}
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="all">All Resources</option>
              {Object.keys(groupedPermissions).sort().map(resource => (
                <option key={resource} value={resource}>
                  {resource.charAt(0).toUpperCase() + resource.slice(1).replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Matrix Table */}
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading matrix...</div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-100 dark:bg-slate-800 sticky top-0">
                    <tr>
                      <th className="text-left p-3 font-semibold w-64 border-r">Permission</th>
                      {roles.map(role => {
                        const isCustomRole = !role.is_system_role && !role.is_system;
                        return (
                          <th 
                            key={role.id} 
                            className="text-center p-2 font-semibold border-r"
                            style={{ 
                              minWidth: '45px', 
                              maxWidth: '60px',
                              width: '50px',
                              color: isCustomRole ? '#b91c1c' : 'inherit',
                              fontWeight: isCustomRole ? '700' : '600'
                            }}
                            title={ROLE_ABBREV[role.code]?.full || role.name}
                          >
                            <div className="text-xs truncate">
                              {ROLE_ABBREV[role.code]?.abbrev || role.code.substring(0, 7).toUpperCase()}
                            </div>
                          </th>
                        );
                      })}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResources.map((resource, idx) => (
                      <Fragment key={resource}>
                        {/* Resource Header Row */}
                        <tr className="bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800">
                          <td 
                            colSpan={roles.length + 1} 
                            className="p-2 font-semibold cursor-pointer"
                            onClick={() => toggleSection(resource)}
                          >
                            <div className="flex items-center gap-2">
                              {expandedSections.has(resource) ? (
                                <ChevronDown className="h-4 w-4" />
                              ) : (
                                <ChevronRight className="h-4 w-4" />
                              )}
                              <span className="uppercase text-xs tracking-wide">
                                {resource.replace('_', ' ')} ({groupedPermissions[resource].length} permissions)
                              </span>
                            </div>
                          </td>
                        </tr>

                        {/* Permission Rows */}
                        {expandedSections.has(resource) && groupedPermissions[resource].map((perm, permIdx) => {
                          const permKey = `${perm.resource_type}.${perm.action}.${perm.scope}`;
                          const isModified = Object.values(changes).some((c: any) => 
                            c.added.includes(perm.id) || c.removed.includes(perm.id)
                          );

                          return (
                            <tr 
                              key={perm.id}
                              className={`border-t hover:bg-slate-50 dark:hover:bg-slate-900 ${
                                permIdx % 2 === 0 ? 'bg-white dark:bg-slate-950' : 'bg-slate-50/50 dark:bg-slate-900/50'
                              }`}
                            >
                              <td className="p-2 pl-6 border-r">
                                <div className="text-xs font-mono text-slate-600 dark:text-slate-400">
                                  {permKey}
                                </div>
                                <div className="text-xs text-muted-foreground mt-0.5">
                                  {perm.description}
                                </div>
                              </td>
                              {roles.map(role => {
                                const hasPermission = assignments[role.id]?.includes(perm.id) || false;
                                const isSystemRole = role.is_system_role;
                                const canEdit = !isSystemRole || canEditSystemRoles;
                                const changeKey = `${role.id}_${perm.id}`;
                                const isChanged = changes[role.id]?.added.includes(perm.id) || 
                                                 changes[role.id]?.removed.includes(perm.id);

                                return (
                                  <td 
                                    key={role.id}
                                    className={`text-center p-2 border-r ${
                                      isChanged ? 'bg-yellow-100 dark:bg-yellow-900/30' : ''
                                    }`}
                                  >
                                    {canEdit ? (
                                      <div className="flex items-center justify-center">
                                        <Checkbox
                                          checked={hasPermission}
                                          onCheckedChange={() => togglePermission(role.id, perm.id, role.code, isSystemRole)}
                                          className="h-4 w-4"
                                        />
                                      </div>
                                    ) : (
                                      <div 
                                        className="flex items-center justify-center"
                                        title="Only Developer can edit system role permissions"
                                      >
                                        <Lock className="h-3 w-3 text-muted-foreground" />
                                      </div>
                                    )}
                                  </td>
                                );
                              })}
                            </tr>
                          );
                        })}
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>

              {filteredResources.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No permissions match your search criteria
                </div>
              )}
            </div>
          )}

          {/* Legend */}
          <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg text-xs space-y-1">
            <div className="font-semibold mb-2">Legend:</div>
            <div className="flex items-center gap-2">
              <Checkbox checked className="h-3 w-3" disabled />
              <span>Enabled</span>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox className="h-3 w-3" disabled />
              <span>Disabled</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="h-3 w-3" />
              <span>System role (Developer-only edit)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-8 bg-yellow-100 dark:bg-yellow-900/30 border" />
              <span>Modified (pending save)</span>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-3 text-xs text-muted-foreground text-center">
            {permissions.length} total permissions × {roles.length} roles = {permissions.length * roles.length} assignments
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PermissionMatrixTable;
