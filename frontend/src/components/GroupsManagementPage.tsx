import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Plus, Edit2, Trash2, X, Search, UserPlus, UserMinus } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const GroupsManagementPage: React.FC = () => {
  const [groups, setGroups] = useState<any[]>([]);
  const [allUsers, setAllUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showMembersModal, setShowMembersModal] = useState<boolean>(false);
  const [selectedGroup, setSelectedGroup] = useState<any | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'team'
  });

  useEffect(() => {
    fetchGroups();
    fetchUsers();
  }, []);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`${API_BASE_URL}/api/groups`, { headers });
      setGroups(response.data.groups || []);
    } catch (err: unknown) {
      console.error('Error fetching groups:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`${API_BASE_URL}/api/users`, { headers });
      setAllUsers(response.data.users || []);
    } catch (err: unknown) {
      console.error('Error fetching users:', err);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(`${API_BASE_URL}/api/groups`, formData, { headers });
      
      setShowCreateModal(false);
      setFormData({ name: '', description: '', type: 'team' });
      fetchGroups();
    } catch (err: unknown) {
      console.error('Error creating group:', err);
      alert(err.response?.data?.detail || 'Failed to create group');
    }
  };

  const handleUpdateGroup = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.put(
        `${API_BASE_URL}/api/groups/${selectedGroup.id}`,
        formData,
        { headers }
      );
      
      setShowEditModal(false);
      setSelectedGroup(null);
      setFormData({ name: '', description: '', type: 'team' });
      fetchGroups();
    } catch (err: unknown) {
      console.error('Error updating group:', err);
      alert(err.response?.data?.detail || 'Failed to update group');
    }
  };

  const handleDeleteGroup = async (groupId) => {
    if (!window.confirm('Are you sure you want to delete this group?')) return;
    
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(`${API_BASE_URL}/api/groups/${groupId}`, { headers });
      fetchGroups();
    } catch (err: unknown) {
      console.error('Error deleting group:', err);
      alert(err.response?.data?.detail || 'Failed to delete group');
    }
  };

  const handleAddMember = async (userId) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.post(
        `${API_BASE_URL}/api/groups/${selectedGroup.id}/members`,
        { user_id: userId },
        { headers }
      );
      
      // Refresh group data
      const response = await axios.get(
        `${API_BASE_URL}/api/groups/${selectedGroup.id}`,
        { headers }
      );
      setSelectedGroup(response.data);
    } catch (err: unknown) {
      console.error('Error adding member:', err);
      alert(err.response?.data?.detail || 'Failed to add member');
    }
  };

  const handleRemoveMember = async (userId) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      await axios.delete(
        `${API_BASE_URL}/api/groups/${selectedGroup.id}/members/${userId}`,
        { headers }
      );
      
      // Refresh group data
      const response = await axios.get(
        `${API_BASE_URL}/api/groups/${selectedGroup.id}`,
        { headers }
      );
      setSelectedGroup(response.data);
    } catch (err: unknown) {
      console.error('Error removing member:', err);
      alert(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const openEditModal = (group) => {
    setSelectedGroup(group);
    setFormData({
      name: group.name,
      description: group.description || '',
      type: group.type || 'team'
    });
    setShowEditModal(true);
  };

  const openMembersModal = async (group) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(
        `${API_BASE_URL}/api/groups/${group.id}`,
        { headers }
      );
      setSelectedGroup(response.data);
      setShowMembersModal(true);
    } catch (err: unknown) {
      console.error('Error fetching group details:', err);
    }
  };

  const filteredGroups = groups.filter(group =>
    group.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    group.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getGroupTypeColor = (type) => {
    const colors = {
      team: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      department: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      project: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      custom: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
    };
    return colors[type] || colors.custom;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-600" />
              Groups & Teams
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Organize users into teams and departments
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Group
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search groups..."
            className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-400"
          />
        </div>

        {/* Groups Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredGroups.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 dark:text-gray-700 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchQuery ? 'No groups found matching your search' : 'No groups created yet'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGroups.map((group) => (
              <div
                key={group.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {group.name}
                    </h3>
                    <span className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${getGroupTypeColor(group.type)}`}>
                      {group.type}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openEditModal(group)}
                      className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteGroup(group.id)}
                      className="p-2 text-gray-600 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {group.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {group.description}
                  </p>
                )}

                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Users className="w-4 h-4" />
                    <span>{group.member_count || 0} members</span>
                  </div>
                  
                  <button
                    onClick={() => openMembersModal(group)}
                    className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    Manage Members
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Group Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Create Group</h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setFormData({ name: '', description: '', type: 'team' });
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateGroup} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Group Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                    placeholder="Engineering Team"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                    placeholder="Brief description of the group"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Type
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  >
                    <option value="team">Team</option>
                    <option value="department">Department</option>
                    <option value="project">Project</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setFormData({ name: '', description: '', type: 'team' });
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create Group
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Group Modal */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Edit Group</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedGroup(null);
                    setFormData({ name: '', description: '', type: 'team' });
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleUpdateGroup} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Group Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Type
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white"
                  >
                    <option value="team">Team</option>
                    <option value="department">Department</option>
                    <option value="project">Project</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedGroup(null);
                      setFormData({ name: '', description: '', type: 'team' });
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Update Group
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Members Management Modal */}
        {showMembersModal && selectedGroup && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Manage Members
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {selectedGroup.name}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowMembersModal(false);
                    setSelectedGroup(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Current Members */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                    Current Members ({selectedGroup.members?.length || 0})
                  </h3>
                  <div className="space-y-2">
                    {selectedGroup.members && selectedGroup.members.length > 0 ? (
                      selectedGroup.members.map((member) => (
                        <div
                          key={member.user_id}
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {member.name?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">
                                {member.name}
                              </p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {member.email}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleRemoveMember(member.user_id)}
                            className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                          >
                            <UserMinus className="w-4 h-4" />
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                        No members in this group yet
                      </p>
                    )}
                  </div>
                </div>

                {/* Add Members */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                    Add Members
                  </h3>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {allUsers
                      .filter(user => !selectedGroup.members?.some(m => m.user_id === user.id))
                      .map((user) => (
                        <div
                          key={user.id}
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {user.name?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">
                                {user.name}
                              </p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {user.email}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleAddMember(user.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg"
                          >
                            <UserPlus className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupsManagementPage;
